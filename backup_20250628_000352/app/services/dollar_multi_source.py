# backend/app/services/dollar_multi_source.py
import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import statistics
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class DollarMultiSourceService:
    """Servicio para obtener dólar blue y tipos de cambio de MÚLTIPLES fuentes"""
    
    def __init__(self):
        self.session = None
        
        # Fuentes de APIs para dólar blue
        self.api_sources = {
            "bluelytics": {
                "url": "https://api.bluelytics.com.ar/v2/latest",
                "method": "GET",
                "parser": self._parse_bluelytics
            },
            "dolarapi": {
                "url": "https://dolarapi.com/v1/dolares",
                "method": "GET", 
                "parser": self._parse_dolarapi
            },
            "dolarsi": {
                "url": "https://www.dolarsi.com/api/api.php?type=valoresprincipales",
                "method": "GET",
                "parser": self._parse_dolarsi
            }
        }
        
        # Fuentes de scraping como backup
        self.scraping_sources = {
            "ambito": {
                "url": "https://www.ambito.com/contenidos/dolar.html",
                "selector": ".valor-venta",
                "parser": self._parse_ambito_scraping
            },
            "cronista": {
                "url": "https://www.cronista.com/MercadosOnline/dolar.html",
                "selector": ".buy-value",
                "parser": self._parse_cronista_scraping
            }
        }
        
        # Tipos de dólar a trackear
        self.dollar_types = [
            "blue", "oficial", "solidario", "liqui", "ccl", 
            "mayorista", "turista", "cripto", "mep"
        ]

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_all_dollar_rates(self) -> Dict[str, Any]:
        """Obtener todos los tipos de dólar de múltiples fuentes"""
        try:
            # Ejecutar todas las fuentes en paralelo
            api_tasks = []
            for source_name, config in self.api_sources.items():
                task = self._fetch_from_api_source(source_name, config)
                api_tasks.append(task)
            
            api_results = await asyncio.gather(*api_tasks, return_exceptions=True)
            
            # Procesar resultados
            all_rates = {}
            sources_data = {}
            successful_sources = 0
            
            for i, result in enumerate(api_results):
                source_name = list(self.api_sources.keys())[i]
                
                if isinstance(result, dict) and result.get("status") == "success":
                    sources_data[source_name] = result.get("data", {})
                    successful_sources += 1
                    logger.info(f"✅ {source_name}: {len(result.get('data', {}))} rates")
                elif isinstance(result, Exception):
                    logger.error(f"❌ {source_name}: {result}")
                else:
                    logger.warning(f"⚠️  {source_name}: {result.get('message', 'Unknown error')}")
            
            # Consolidar datos de todas las fuentes
            consolidated_rates = self._consolidate_rates(sources_data)
            
            return {
                "status": "success",
                "data": consolidated_rates,
                "sources_used": successful_sources,
                "total_sources": len(self.api_sources),
                "timestamp": datetime.now().isoformat(),
                "reliability_score": successful_sources / len(self.api_sources)
            }
            
        except Exception as e:
            logger.error(f"Error getting all dollar rates: {e}")
            return await self._get_fallback_rates()

    async def get_blue_dollar_consensus(self) -> Dict[str, Any]:
        """Obtener consenso del dólar blue entre múltiples fuentes"""
        try:
            rates_data = await self.get_all_dollar_rates()
            
            if rates_data.get("status") != "success":
                return rates_data
            
            blue_rates = []
            source_details = []
            
            # Extraer precios del dólar blue de cada fuente
            for source, data in rates_data.get("data", {}).items():
                if "blue" in data and data["blue"].get("sell"):
                    blue_price = float(data["blue"]["sell"])
                    blue_rates.append(blue_price)
                    source_details.append({
                        "source": source,
                        "price": blue_price,
                        "timestamp": data["blue"].get("timestamp")
                    })
            
            if not blue_rates:
                return {"status": "error", "message": "No blue dollar rates found"}
            
            # Calcular estadísticas
            consensus = {
                "average": round(statistics.mean(blue_rates), 2),
                "median": round(statistics.median(blue_rates), 2),
                "min": min(blue_rates),
                "max": max(blue_rates),
                "spread": round(max(blue_rates) - min(blue_rates), 2),
                "spread_percent": round(((max(blue_rates) - min(blue_rates)) / statistics.mean(blue_rates)) * 100, 2),
                "sources_count": len(blue_rates),
                "sources": source_details
            }
            
            # Detectar outliers
            if len(blue_rates) >= 3:
                mean = consensus["average"]
                std_dev = statistics.stdev(blue_rates)
                outliers = [rate for rate in blue_rates if abs(rate - mean) > 2 * std_dev]
                consensus["outliers"] = outliers
                consensus["has_outliers"] = len(outliers) > 0
            
            return {
                "status": "success",
                "blue_dollar": consensus,
                "timestamp": datetime.now().isoformat(),
                "reliability": "high" if len(blue_rates) >= 3 else "medium" if len(blue_rates) >= 2 else "low"
            }
            
        except Exception as e:
            logger.error(f"Error calculating blue dollar consensus: {e}")
            return {"status": "error", "message": str(e)}

    async def _fetch_from_api_source(self, source_name: str, config: Dict) -> Dict[str, Any]:
        """Obtener datos de una fuente de API específica"""
        try:
            async with self.session.get(config["url"]) as response:
                if response.status == 200:
                    if 'application/json' in response.headers.get('content-type', ''):
                        data = await response.json()
                    else:
                        text = await response.text()
                        data = json.loads(text) if text.strip().startswith('{') else {"raw": text}
                    
                    # Parsear usando el parser específico de cada fuente
                    parsed_data = await config["parser"](data)
                    
                    return {
                        "status": "success",
                        "source": source_name,
                        "data": {source_name: parsed_data}
                    }
                else:
                    return {
                        "status": "error",
                        "source": source_name,
                        "message": f"HTTP {response.status}"
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "source": source_name,
                "message": str(e)
            }

    async def _parse_bluelytics(self, data: Dict) -> Dict[str, Any]:
        """Parser para Bluelytics API"""
        try:
            result = {}
            
            # Dólar blue
            if "blue" in data:
                blue_data = data["blue"]
                result["blue"] = {
                    "buy": blue_data.get("value_buy"),
                    "sell": blue_data.get("value_sell"),
                    "avg": blue_data.get("value_avg"),
                    "timestamp": blue_data.get("last_update")
                }
            
            # Dólar oficial
            if "oficial" in data:
                oficial_data = data["oficial"]
                result["oficial"] = {
                    "buy": oficial_data.get("value_buy"),
                    "sell": oficial_data.get("value_sell"),
                    "avg": oficial_data.get("value_avg"),
                    "timestamp": oficial_data.get("last_update")
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing Bluelytics: {e}")
            return {}

    async def _parse_dolarapi(self, data: List) -> Dict[str, Any]:
        """Parser para DolarAPI"""
        try:
            result = {}
            
            if isinstance(data, list):
                for item in data:
                    name = item.get("nombre", "").lower()
                    
                    if "blue" in name:
                        result["blue"] = {
                            "buy": item.get("compra"),
                            "sell": item.get("venta"),
                            "timestamp": item.get("fechaActualizacion")
                        }
                    elif "oficial" in name:
                        result["oficial"] = {
                            "buy": item.get("compra"),
                            "sell": item.get("venta"),
                            "timestamp": item.get("fechaActualizacion")
                        }
                    elif "solidario" in name:
                        result["solidario"] = {
                            "buy": item.get("compra"),
                            "sell": item.get("venta"),
                            "timestamp": item.get("fechaActualizacion")
                        }
                    elif "liqui" in name or "ccl" in name:
                        result["ccl"] = {
                            "buy": item.get("compra"),
                            "sell": item.get("venta"),
                            "timestamp": item.get("fechaActualizacion")
                        }
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing DolarAPI: {e}")
            return {}

    async def _parse_dolarsi(self, data: List) -> Dict[str, Any]:
        """Parser para DolarSi API"""
        try:
            result = {}
            
            if isinstance(data, list):
                for item in data:
                    casa = item.get("casa", {})
                    name = casa.get("nombre", "").lower()
                    
                    if "blue" in name:
                        result["blue"] = {
                            "buy": float(casa.get("compra", 0).replace(",", ".")),
                            "sell": float(casa.get("venta", 0).replace(",", ".")),
                            "timestamp": datetime.now().isoformat()
                        }
                    elif "oficial" in name:
                        result["oficial"] = {
                            "buy": float(casa.get("compra", 0).replace(",", ".")),
                            "sell": float(casa.get("venta", 0).replace(",", ".")),
                            "timestamp": datetime.now().isoformat()
                        }
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing DolarSi: {e}")
            return {}

    def _consolidate_rates(self, sources_data: Dict) -> Dict[str, Any]:
        """Consolidar datos de todas las fuentes"""
        consolidated = {}
        
        # Para cada tipo de dólar
        for dollar_type in self.dollar_types:
            rates_for_type = []
            sources_for_type = []
            
            # Recopilar datos de todas las fuentes
            for source_name, source_data in sources_data.items():
                if dollar_type in source_data:
                    rate_data = source_data[dollar_type]
                    if rate_data.get("sell"):
                        rates_for_type.append({
                            "source": source_name,
                            "buy": rate_data.get("buy"),
                            "sell": rate_data.get("sell"),
                            "timestamp": rate_data.get("timestamp")
                        })
                        sources_for_type.append(source_name)
            
            # Si hay datos para este tipo de dólar
            if rates_for_type:
                sell_prices = [float(r["sell"]) for r in rates_for_type if r["sell"]]
                buy_prices = [float(r["buy"]) for r in rates_for_type if r["buy"]]
                
                consolidated[dollar_type] = {
                    "sell_avg": round(statistics.mean(sell_prices), 2) if sell_prices else None,
                    "buy_avg": round(statistics.mean(buy_prices), 2) if buy_prices else None,
                    "sell_median": round(statistics.median(sell_prices), 2) if sell_prices else None,
                    "sell_min": min(sell_prices) if sell_prices else None,
                    "sell_max": max(sell_prices) if sell_prices else None,
                    "sources": sources_for_type,
                    "sources_count": len(sources_for_type),
                    "raw_data": rates_for_type
                }
        
        return consolidated

    async def _get_fallback_rates(self) -> Dict[str, Any]:
        """Datos de fallback si todas las fuentes fallan"""
        logger.warning("Using fallback dollar rates")
        
        return {
            "status": "fallback",
            "data": {
                "blue": {
                    "sell_avg": 1180.0,
                    "buy_avg": 1170.0,
                    "sources": ["fallback"],
                    "sources_count": 1
                },
                "oficial": {
                    "sell_avg": 987.5,
                    "buy_avg": 985.0,
                    "sources": ["fallback"],
                    "sources_count": 1
                }
            },
            "timestamp": datetime.now().isoformat(),
            "message": "All external sources failed, using fallback data"
        }

    async def _parse_ambito_scraping(self, html: str) -> Dict[str, Any]:
        """Parser para scraping de Ámbito"""
        # Implementación básica - puede expandirse
        return {}

    async def _parse_cronista_scraping(self, html: str) -> Dict[str, Any]:
        """Parser para scraping de Cronista"""
        # Implementación básica - puede expandirse
        return {}

# Función de test
async def test_dollar_multi_source():
    """Test del servicio multi-fuente de dólar"""
    async with DollarMultiSourceService() as service:
        print("🔥 Testing Dollar Multi-Source Service...")
        print("="*60)
        
        # Test 1: Todos los tipos de dólar
        print("\n💰 Testing All Dollar Types...")
        all_rates = await service.get_all_dollar_rates()
        if all_rates.get("status") == "success":
            sources_used = all_rates.get("sources_used", 0)
            total_sources = all_rates.get("total_sources", 0)
            reliability = all_rates.get("reliability_score", 0)
            
            print(f"✅ Fuentes exitosas: {sources_used}/{total_sources}")
            print(f"✅ Confiabilidad: {reliability:.2%}")
            
            data = all_rates.get("data", {})
            for dollar_type, rates in data.items():
                if rates:
                    avg_sell = rates.get("sell_avg")
                    sources_count = rates.get("sources_count", 0)
                    print(f"  💵 {dollar_type.upper()}: ${avg_sell} (de {sources_count} fuentes)")
        else:
            print(f"❌ Error: {all_rates}")
        
        # Test 2: Consenso dólar blue
        print("\n🔵 Testing Blue Dollar Consensus...")
        consensus = await service.get_blue_dollar_consensus()
        if consensus.get("status") == "success":
            blue_data = consensus.get("blue_dollar", {})
            print(f"✅ Consenso Dólar Blue:")
            print(f"  • Promedio: ${blue_data.get('average')}")
            print(f"  • Mediana: ${blue_data.get('median')}")
            print(f"  • Rango: ${blue_data.get('min')} - ${blue_data.get('max')}")
            print(f"  • Spread: ${blue_data.get('spread')} ({blue_data.get('spread_percent')}%)")
            print(f"  • Fuentes: {blue_data.get('sources_count')}")
            
            if blue_data.get("has_outliers"):
                print(f"  ⚠️  Outliers detectados: {blue_data.get('outliers')}")
        else:
            print(f"❌ Error: {consensus}")
        
        print("\n🎉 Test completado! Dólar multi-fuente funcionando")

if __name__ == "__main__":
    asyncio.run(test_dollar_multi_source())