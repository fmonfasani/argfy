# backend/app/services/bcra_real_data_service.py
import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from app.models import EconomicIndicator, HistoricalData
from app.database import get_db
import json

logger = logging.getLogger(__name__)

class BCRARealDataService:
    """Servicio para obtener datos REALES del BCRA"""
    
    def __init__(self):
        self.base_urls = {
            "monetarias": "https://api.bcra.gob.ar/estadisticas/v3.0/Monetarias",
            "cotizaciones": "https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones",
            "deudores": "https://api.bcra.gob.ar/centraldedeudores/v1.0/Deudas",
            "cheques": "https://api.bcra.gob.ar/cheques/v1.0"
        }
        self.session = None
        
        # Mapeo de variables importantes
        self.variables_clave = {
            1: "reservas_internacionales",  # Reservas en USD millones
            4: "usd_minorista",            # USD Minorista
            5: "usd_mayorista",            # USD Mayorista  
            6: "tasa_politica_nominal",     # Tasa Política Monetaria (n.a.)
            34: "tasa_politica_efectiva",   # Tasa Política Monetaria (e.a.)
            27: "inflacion_mensual",        # Inflación mensual
            28: "inflacion_interanual",     # Inflación interanual
            7: "badlar_privados",          # BADLAR bancos privados
            15: "base_monetaria",          # Base monetaria
            21: "depositos_total"          # Depósitos totales
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_variables_monetarias(self) -> Dict[str, Any]:
        """Obtener todas las variables monetarias del BCRA"""
        try:
            url = self.base_urls["monetarias"]
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Procesar y estructurar datos
                    variables = {}
                    for item in data.get("results", []):
                        var_id = item.get("idVariable")
                        
                        # Solo procesar variables que nos interesan
                        if var_id in self.variables_clave:
                            key = self.variables_clave[var_id]
                            variables[key] = {
                                "id": var_id,
                                "valor": item.get("valor"),
                                "descripcion": item.get("descripcion"),
                                "fecha": item.get("fecha"),
                                "categoria": item.get("categoria")
                            }
                    
                    return {
                        "status": "success",
                        "variables": variables,
                        "total_disponibles": len(data.get("results", [])),
                        "timestamp": datetime.now().isoformat(),
                        "source": "BCRA_MONETARIAS"
                    }
                else:
                    logger.error(f"Error BCRA monetarias: HTTP {response.status}")
                    return {"status": "error", "code": response.status}
                    
        except Exception as e:
            logger.error(f"Error fetching BCRA variables: {e}")
            return {"status": "error", "message": str(e)}

    async def get_cotizaciones_oficiales(self) -> Dict[str, Any]:
        """Obtener cotizaciones oficiales del BCRA"""
        try:
            url = self.base_urls["cotizaciones"]
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Procesar cotizaciones
                    cotizaciones = {}
                    for item in data.get("results", {}).get("detalle", []):
                        codigo = item.get("codigoMoneda")
                        cotizacion = item.get("tipoCotizacion", 0)
                        
                        if codigo and cotizacion > 0:
                            cotizaciones[codigo] = {
                                "codigo": codigo,
                                "descripcion": item.get("descripcion"),
                                "cotizacion": cotizacion,
                                "tipo_pase": item.get("tipoPase", 0)
                            }
                    
                    return {
                        "status": "success",
                        "fecha": data.get("results", {}).get("fecha"),
                        "cotizaciones": cotizaciones,
                        "timestamp": datetime.now().isoformat(),
                        "source": "BCRA_COTIZACIONES"
                    }
                else:
                    logger.error(f"Error BCRA cotizaciones: HTTP {response.status}")
                    return {"status": "error", "code": response.status}
                    
        except Exception as e:
            logger.error(f"Error fetching BCRA cotizaciones: {e}")
            return {"status": "error", "message": str(e)}

    async def get_variable_historica(self, variable_id: int, dias: int = 30) -> Dict[str, Any]:
        """Obtener datos históricos de una variable específica"""
        try:
            fecha_hasta = datetime.now().strftime("%Y-%m-%d")
            fecha_desde = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
            
            url = f"{self.base_urls['monetarias']}/{variable_id}"
            params = {
                "desde": fecha_desde,
                "hasta": fecha_hasta,
                "limit": 1000
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "status": "success",
                        "variable_id": variable_id,
                        "datos": data.get("results", []),
                        "metadata": data.get("metadata", {}),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"status": "error", "code": response.status}
                    
        except Exception as e:
            logger.error(f"Error fetching historical data for {variable_id}: {e}")
            return {"status": "error", "message": str(e)}

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Obtener datos consolidados para el dashboard"""
        try:
            # Ejecutar consultas en paralelo
            tasks = [
                self.get_variables_monetarias(),
                self.get_cotizaciones_oficiales()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            variables = results[0] if not isinstance(results[0], Exception) else {}
            cotizaciones = results[1] if not isinstance(results[1], Exception) else {}
            
            # Crear estructura para el dashboard
            dashboard = {
                "indicadores_principales": {},
                "cotizaciones": {},
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            # Procesar variables monetarias
            if variables.get("status") == "success":
                vars_data = variables.get("variables", {})
                
                # USD Oficial (usar mayorista como principal)
                if "usd_mayorista" in vars_data:
                    dashboard["indicadores_principales"]["usd_oficial"] = {
                        "value": vars_data["usd_mayorista"]["valor"],
                        "label": "USD Oficial",
                        "change": 0,  # Calcular después con históricos
                        "source": "BCRA",
                        "updated": vars_data["usd_mayorista"]["fecha"]
                    }
                
                # Reservas BCRA
                if "reservas_internacionales" in vars_data:
                    dashboard["indicadores_principales"]["reservas_bcra"] = {
                        "value": vars_data["reservas_internacionales"]["valor"],
                        "label": "Reservas BCRA (USD Mill.)",
                        "change": 0,
                        "source": "BCRA",
                        "updated": vars_data["reservas_internacionales"]["fecha"]
                    }
                
                # Tasa BCRA
                if "tasa_politica_nominal" in vars_data:
                    dashboard["indicadores_principales"]["tasa_bcra"] = {
                        "value": vars_data["tasa_politica_nominal"]["valor"],
                        "label": "Tasa BCRA (%)",
                        "change": 0,
                        "source": "BCRA",
                        "updated": vars_data["tasa_politica_nominal"]["fecha"]
                    }
                
                # Inflación
                if "inflacion_mensual" in vars_data:
                    dashboard["indicadores_principales"]["inflacion"] = {
                        "value": vars_data["inflacion_mensual"]["valor"],
                        "label": "Inflación Mensual (%)",
                        "change": 0,
                        "source": "BCRA",
                        "updated": vars_data["inflacion_mensual"]["fecha"]
                    }
            
            # Procesar cotizaciones
            if cotizaciones.get("status") == "success":
                cotiz_data = cotizaciones.get("cotizaciones", {})
                
                # Principales monedas
                monedas_principales = ["USD", "EUR", "GBP", "BRL", "JPY"]
                for moneda in monedas_principales:
                    if moneda in cotiz_data:
                        dashboard["cotizaciones"][moneda] = {
                            "value": cotiz_data[moneda]["cotizacion"],
                            "descripcion": cotiz_data[moneda]["descripcion"],
                            "source": "BCRA",
                            "updated": cotizaciones.get("fecha")
                        }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {"status": "error", "message": str(e)}

    async def save_to_database(self, dashboard_data: Dict) -> bool:
        """Guardar datos en la base de datos"""
        try:
            db = next(get_db())
            
            # Guardar indicadores principales
            for key, data in dashboard_data.get("indicadores_principales", {}).items():
                indicator = EconomicIndicator(
                    indicator_type=key,
                    value=data["value"],
                    source="BCRA",
                    date=datetime.now(),
                    is_active=True
                )
                db.add(indicator)
            
            # Guardar cotizaciones
            for key, data in dashboard_data.get("cotizaciones", {}).items():
                indicator = EconomicIndicator(
                    indicator_type=f"cotizacion_{key.lower()}",
                    value=data["value"],
                    source="BCRA",
                    date=datetime.now(),
                    is_active=True
                )
                db.add(indicator)
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            db.rollback()
            return False
        finally:
            db.close()


# Test del servicio completo
async def test_bcra_real_service():
    async with BCRARealDataService() as service:
        print("🔥 Testing BCRA Real Data Service...")
        
        # Test variables monetarias
        print("\n📊 Testing Variables Monetarias...")
        variables = await service.get_variables_monetarias()
        if variables.get("status") == "success":
            print(f"✅ Variables obtenidas: {len(variables.get('variables', {}))}")
            for key, data in variables.get("variables", {}).items():
                print(f"  • {key}: {data['valor']} ({data['fecha']})")
        else:
            print(f"❌ Error: {variables}")
        
        # Test cotizaciones
        print("\n💱 Testing Cotizaciones...")
        cotizaciones = await service.get_cotizaciones_oficiales()
        if cotizaciones.get("status") == "success":
            print(f"✅ Cotizaciones obtenidas: {len(cotizaciones.get('cotizaciones', {}))}")
            for moneda, data in list(cotizaciones.get("cotizaciones", {}).items())[:5]:
                print(f"  • {moneda}: ${data['cotizacion']}")
        else:
            print(f"❌ Error: {cotizaciones}")
        
        # Test dashboard completo
        print("\n🎯 Testing Dashboard Data...")
        dashboard = await service.get_dashboard_data()
        if dashboard.get("status") == "success":
            print("✅ Dashboard data generado exitosamente")
            print(f"  • Indicadores: {len(dashboard.get('indicadores_principales', {}))}")
            print(f"  • Cotizaciones: {len(dashboard.get('cotizaciones', {}))}")
        else:
            print(f"❌ Error: {dashboard}")

if __name__ == "__main__":
    asyncio.run(test_bcra_real_service())