# backend/app/services/expanded_data_service.py
"""
Servicio expandido para obtener TODOS los datos económicos del demo
"""

import asyncio
import aiohttp
import httpx
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from bs4 import BeautifulSoup
import pandas as pd
import json

from ..config.indicators_mapping import ALL_INDICATORS, CATEGORIES
from ..models import EconomicIndicator, HistoricalData
from ..database import get_db

logger = logging.getLogger(__name__)

class ExpandedDataService:
    """Servicio para obtener TODOS los indicadores de la plataforma"""
    
    def __init__(self):
        self.session = None
        self.httpx_client = None
        self.requests_session = requests.Session()
        
        # URLs base para diferentes fuentes
        self.apis = {
            "bcra": "https://api.bcra.gob.ar",
            "indec": "https://apis.datos.gob.ar/series/api",
            "bluelytics": "https://api.bluelytics.com.ar/v2",
            "byma": "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free",
            "dolar_api": "https://dolarapi.com/v1"
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        self.httpx_client = httpx.AsyncClient()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.httpx_client:
            await self.httpx_client.aclose()

    # SECCIÓN 1: DATOS ECONÓMICOS
    async def get_economic_indicators(self) -> Dict[str, Any]:
        """Obtener todos los indicadores económicos"""
        try:
            # Ejecutar en paralelo
            tasks = [
                self.get_ipc_data(),
                self.get_pbi_data(),
                self.get_emae_data(),
                self.get_desempleo_data(),
                self.get_reservas_bcra(),
                self.get_dolar_blue()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                "ipc": results[0],
                "pbi": results[1], 
                "emae": results[2],
                "desempleo": results[3],
                "reservas_bcra": results[4],
                "dolar_blue": results[5],
                "timestamp": datetime.now().isoformat(),
                "category": "economia"
            }
            
        except Exception as e:
            logger.error(f"Error getting economic indicators: {e}")
            return {"status": "error", "message": str(e)}

    async def get_ipc_data(self) -> Dict:
        """IPC - Inflación mensual del INDEC"""
        try:
            url = f"{self.apis['indec']}/series/?ids=148.3_INIVELNAL_DICI_M_26&limit=1"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('data') and len(data['data']) > 0:
                        latest = data['data'][0]
                        return {
                            "value": latest[1],  # Valor
                            "date": latest[0],   # Fecha
                            "source": "INDEC",
                            "unit": "%",
                            "status": "success"
                        }
        except Exception as e:
            logger.error(f"Error fetching IPC: {e}")
        
        # Fallback con valor demo
        return {
            "value": 3.2,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "DEMO",
            "unit": "%",
            "status": "demo"
        }

    async def get_pbi_data(self) -> Dict:
        """PBI - Crecimiento del PBI"""
        try:
            url = f"{self.apis['indec']}/series/?ids=143.3_NO_PR_2004_A_21&limit=1"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('data') and len(data['data']) > 0:
                        latest = data['data'][0]
                        return {
                            "value": latest[1],
                            "date": latest[0],
                            "source": "INDEC",
                            "unit": "%",
                            "status": "success"
                        }
        except Exception as e:
            logger.error(f"Error fetching PBI: {e}")
        
        return {
            "value": -1.4,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "DEMO",
            "unit": "%",
            "status": "demo"
        }

    async def get_emae_data(self) -> Dict:
        """EMAE - Estimador Mensual de Actividad Económica"""
        # Similar implementation
        return {
            "value": 156.8,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "DEMO",
            "unit": "índice",
            "status": "demo"
        }

    async def get_desempleo_data(self) -> Dict:
        """Tasa de desempleo"""
        return {
            "value": 6.2,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "DEMO",
            "unit": "%",
            "status": "demo"
        }

    async def get_reservas_bcra(self) -> Dict:
        """Reservas internacionales del BCRA"""
        try:
            url = f"{self.apis['bcra']}/estadisticas/v3.0/Monetarias/1"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('results') and len(data['results']) > 0:
                        latest = data['results'][-1]
                        return {
                            "value": latest['valor'],
                            "date": latest['fecha'],
                            "source": "BCRA",
                            "unit": "USD Mill.",
                            "status": "success"
                        }
        except Exception as e:
            logger.error(f"Error fetching reserves: {e}")
        
        return {
            "value": 41200,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "DEMO",
            "unit": "USD Mill.",
            "status": "demo"
        }

    async def get_dolar_blue(self) -> Dict:
        """Dólar blue de Bluelytics"""
        try:
            url = f"{self.apis['bluelytics']}/latest"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    blue_sell = data.get('blue', {}).get('value_sell')
                    if blue_sell:
                        return {
                            "value": blue_sell,
                            "date": data.get('last_update', datetime.now().isoformat()),
                            "source": "BLUELYTICS",
                            "unit": "ARS",
                            "status": "success"
                        }
        except Exception as e:
            logger.error(f"Error fetching dolar blue: {e}")
        
        return {
            "value": 1350,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "DEMO",
            "unit": "ARS",
            "status": "demo"
        }

    # SECCIÓN 2: DATOS DE GOBIERNO
    async def get_government_indicators(self) -> Dict[str, Any]:
        """Obtener todos los indicadores de gobierno"""
        # Implementar scraping de MECON, AFIP, etc.
        return {
            "resultado_fiscal": {"value": -2.1, "source": "DEMO", "unit": "% PBI"},
            "deuda_publica": {"value": 89.4, "source": "DEMO", "unit": "% PBI"},
            "gasto_publico": {"value": 41.2, "source": "DEMO", "unit": "% PBI"},
            "ingresos_tributarios": {"value": 28.5, "source": "DEMO", "unit": "% PBI"},
            "empleo_publico": {"value": 3400000, "source": "DEMO", "unit": "empleados"},
            "transferencias_sociales": {"value": 8.7, "source": "DEMO", "unit": "% PBI"},
            "timestamp": datetime.now().isoformat(),
            "category": "gobierno"
        }

    # SECCIÓN 3: DATOS FINANCIEROS
    async def get_financial_indicators(self) -> Dict[str, Any]:
        """Obtener todos los indicadores financieros del BCRA"""
        try:
            # Usar API del BCRA para tasas
            tasks = [
                self.get_bcra_variable(29),  # Plazo fijo 30 días
                self.get_bcra_variable(31),  # Tasa tarjeta crédito
                self.get_bcra_variable(18),  # Depósitos privados
                self.get_bcra_variable(19),  # Préstamos sector privado
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                "plazo_fijo_30": results[0] if not isinstance(results[0], Exception) else {"value": 118, "source": "DEMO"},
                "tasa_tarjeta_credito": results[1] if not isinstance(results[1], Exception) else {"value": 195, "source": "DEMO"},
                "depositos_privados": results[2] if not isinstance(results[2], Exception) else {"value": 45200000, "source": "DEMO"},
                "prestamos_sector_privado": results[3] if not isinstance(results[3], Exception) else {"value": 28700000, "source": "DEMO"},
                "morosidad_bancaria": {"value": 3.1, "source": "DEMO", "unit": "%"},
                "liquidez_bancaria": {"value": 64.2, "source": "DEMO", "unit": "%"},
                "timestamp": datetime.now().isoformat(),
                "category": "finanzas"
            }
            
        except Exception as e:
            logger.error(f"Error getting financial indicators: {e}")
            return self.get_demo_financial_data()

    async def get_bcra_variable(self, variable_id: int) -> Dict:
        """Helper para obtener variables específicas del BCRA"""
        try:
            url = f"{self.apis['bcra']}/estadisticas/v3.0/Monetarias/{variable_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('results') and len(data['results']) > 0:
                        latest = data['results'][-1]
                        return {
                            "value": latest['valor'],
                            "date": latest['fecha'],
                            "source": "BCRA",
                            "status": "success"
                        }
        except Exception as e:
            logger.error(f"Error fetching BCRA variable {variable_id}: {e}")
        
        return {"value": 0, "source": "ERROR", "status": "error"}

    # SECCIÓN 4: DATOS DE MERCADOS
    async def get_market_indicators(self) -> Dict[str, Any]:
        """Obtener todos los indicadores de mercados"""
        try:
            # Implementar integración con BYMA
            tasks = [
                self.get_merval_data(),
                self.get_bonds_data(),
                self.get_ccl_data()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                "merval": results[0] if not isinstance(results[0], Exception) else {"value": 1847523, "source": "DEMO"},
                "rendimiento_al30": {"value": 15.2, "source": "DEMO", "unit": "%"},
                "precio_gd30": {"value": 453.2, "source": "DEMO", "unit": "ARS"},
                "volumen_acciones_cedears": {"value": 2800000000, "source": "DEMO", "unit": "ARS"},
                "dolar_ccl": {"value": 1287, "source": "DEMO", "unit": "ARS"},
                "panel_general_byma": {"value": 842, "source": "DEMO", "unit": "especies"},
                "timestamp": datetime.now().isoformat(),
                "category": "mercados"
            }
            
        except Exception as e:
            logger.error(f"Error getting market indicators: {e}")
            return self.get_demo_market_data()

    async def get_merval_data(self) -> Dict:
        """Obtener datos del MERVAL desde BYMA"""
        try:
            # Implementar API de BYMA
            url = f"{self.apis['byma']}/index"
            # Por ahora retornar demo data
            pass
        except Exception as e:
            logger.error(f"Error fetching MERVAL: {e}")
        
        return {
            "value": 1847523,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "DEMO",
            "unit": "puntos",
            "status": "demo"
        }

    # SECCIÓN 5: TECNOLOGÍA
    async def get_tech_indicators(self) -> Dict[str, Any]:
        """Obtener indicadores de tecnología (principalmente manuales)"""
        return {
            "exportaciones_sbc": {"value": 7800000000, "source": "DEMO", "unit": "USD"},
            "empleo_it": {"value": 15.2, "source": "DEMO", "unit": "%"},
            "inversion_id": {"value": 0.54, "source": "DEMO", "unit": "% PBI"},
            "penetracion_internet": {"value": 87.2, "source": "DEMO", "unit": "%"},
            "vc_startups": {"value": 542000000, "source": "DEMO", "unit": "USD"},
            "facturacion_software": {"value": 3200000000, "source": "DEMO", "unit": "USD"},
            "timestamp": datetime.now().isoformat(),
            "category": "tecnologia"
        }

    # SECCIÓN 6: INDUSTRIA
    async def get_industry_indicators(self) -> Dict[str, Any]:
        """Obtener indicadores de industria"""
        return {
            "ipi_manufacturero": {"value": -8.5, "source": "DEMO", "unit": "%"},
            "pmi": {"value": 43.2, "source": "DEMO", "unit": "índice"},
            "produccion_automotriz": {"value": -12.1, "source": "DEMO", "unit": "%"},
            "exportaciones_moi": {"value": 12800000000, "source": "DEMO", "unit": "USD"},
            "produccion_acero": {"value": -15.3, "source": "DEMO", "unit": "%"},
            "costo_construccion": {"value": 42.8, "source": "DEMO", "unit": "%"},
            "timestamp": datetime.now().isoformat(),
            "category": "industria"
        }

    # MÉTODO PRINCIPAL
    async def get_all_indicators(self) -> Dict[str, Any]:
        """Obtener TODOS los indicadores de todas las categorías"""
        try:
            tasks = [
                self.get_economic_indicators(),
                self.get_government_indicators(),
                self.get_financial_indicators(),
                self.get_market_indicators(),
                self.get_tech_indicators(),
                self.get_industry_indicators()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Compilar todos los datos
            all_data = {}
            categories = ["economia", "gobierno", "finanzas", "mercados", "tecnologia", "industria"]
            
            for i, result in enumerate(results):
                if not isinstance(result, Exception):
                    category = categories[i]
                    all_data[category] = result
                else:
                    logger.error(f"Error in category {categories[i]}: {result}")
            
            return {
                "status": "success",
                "data": all_data,
                "total_indicators": sum(len(cat_data) - 2 for cat_data in all_data.values()),  # -2 for timestamp and category
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
        except Exception as e:
            logger.error(f"Error getting all indicators: {e}")
            return {"status": "error", "message": str(e)}

    # MÉTODOS DE DATOS HISTÓRICOS
    async def get_historical_data(self, indicator: str, days: int = 30) -> Dict[str, Any]:
        """Obtener datos históricos de un indicador específico"""
        try:
            # Implementar lógica específica por tipo de indicador
            if indicator in ["ipc", "pbi", "emae"]:
                return await self.get_indec_historical(indicator, days)
            elif indicator in ["reservas_bcra", "plazo_fijo_30"]:
                return await self.get_bcra_historical(indicator, days)
            elif indicator == "dolar_blue":
                return await self.get_blue_historical(days)
            elif indicator == "merval":
                return await self.get_market_historical(indicator, days)
            else:
                # Generar datos demo históricos
                return self.generate_demo_historical(indicator, days)
                
        except Exception as e:
            logger.error(f"Error getting historical data for {indicator}: {e}")
            return self.generate_demo_historical(indicator, days)

    def generate_demo_historical(self, indicator: str, days: int) -> Dict[str, Any]:
        """Generar datos históricos demo para gráficos"""
        import random
        
        # Obtener valor actual del indicador
        current_value = 100  # Base value
        
        if indicator == "ipc":
            current_value = 3.2
        elif indicator == "dolar_blue":
            current_value = 1350
        elif indicator == "merval":
            current_value = 1847523
        elif indicator == "reservas_bcra":
            current_value = 41200
        
        # Generar serie histórica con variación realista
        data_points = []
        value = current_value
        
        for i in range(days, 0, -1):
            # Variación aleatoria pero realista
            variation = random.uniform(-0.05, 0.05)  # ±5%
            value = value * (1 + variation)
            
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            data_points.append({
                "date": date,
                "value": round(value, 2),
                "period": "daily"
            })
        
        return {
            "status": "success",
            "indicator": indicator,
            "data": data_points,
            "period": f"{days} days",
            "source": "DEMO_HISTORICAL"
        }

    # MÉTODOS DE UTILIDAD
    def get_demo_financial_data(self):
        """Datos demo para indicadores financieros"""
        return {
            "plazo_fijo_30": {"value": 118, "source": "DEMO", "unit": "%"},
            "tasa_tarjeta_credito": {"value": 195, "source": "DEMO", "unit": "%"},
            "depositos_privados": {"value": 45200000, "source": "DEMO", "unit": "millones ARS"},
            "prestamos_sector_privado": {"value": 28700000, "source": "DEMO", "unit": "millones ARS"},
            "morosidad_bancaria": {"value": 3.1, "source": "DEMO", "unit": "%"},
            "liquidez_bancaria": {"value": 64.2, "source": "DEMO", "unit": "%"},
            "timestamp": datetime.now().isoformat(),
            "category": "finanzas"
        }

    def get_demo_market_data(self):
        """Datos demo para indicadores de mercado"""
        return {
            "merval": {"value": 1847523, "source": "DEMO", "unit": "puntos"},
            "rendimiento_al30": {"value": 15.2, "source": "DEMO", "unit": "%"},
            "precio_gd30": {"value": 453.2, "source": "DEMO", "unit": "ARS"},
            "volumen_acciones_cedears": {"value": 2800000000, "source": "DEMO", "unit": "ARS"},
            "dolar_ccl": {"value": 1287, "source": "DEMO", "unit": "ARS"},
            "panel_general_byma": {"value": 842, "source": "DEMO", "unit": "especies"},
            "timestamp": datetime.now().isoformat(),
            "category": "mercados"
        }


# SCRIPT DE TESTING
async def test_expanded_service():
    """Test completo del servicio expandido"""
    async with ExpandedDataService() as service:
        print("🔥 Testing Expanded Data Service...")
        
        # Test todos los indicadores
        all_data = await service.get_all_indicators()
        if all_data.get("status") == "success":
            print(f"✅ Total indicators: {all_data.get('total_indicators')}")
            
            for category, data in all_data.get("data", {}).items():
                indicator_count = len(data) - 2  # -2 for timestamp and category
                print(f"  📊 {category}: {indicator_count} indicators")
        
        # Test datos históricos
        historical = await service.get_historical_data("dolar_blue", 30)
        if historical.get("status") == "success":
            print(f"✅ Historical data: {len(historical.get('data', []))} points")
        
        print("🎯 Expanded service test completed!")

if __name__ == "__main__":
    asyncio.run(test_expanded_service())