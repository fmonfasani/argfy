# backend/app/services/bcra_expanded_service.py
import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from app.models import EconomicIndicator, HistoricalData
from app.database import get_db
import json

logger = logging.getLogger(__name__)

class BCRAExpandedService:
    """Servicio EXPANDIDO con TODAS las variables del BCRA disponibles"""
    
    def __init__(self):
        self.base_urls = {
            "monetarias": "https://api.bcra.gob.ar/estadisticas/v3.0/Monetarias",
            "cotizaciones": "https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones",
            "principales": "https://api.bcra.gob.ar/estadisticas/v2.0/principalesvariables"
        }
        self.session = None
        
        # VARIABLES EXPANDIDAS - 50+ variables clave del BCRA
        self.variables_completas = {
            # Variables monetarias básicas
            1: {"name": "reservas_internacionales", "label": "Reservas Internacionales", "unit": "USD Mill."},
            2: {"name": "circulacion_monetaria", "label": "Circulación Monetaria", "unit": "ARS Mill."},
            3: {"name": "efectivo_cajas_bancos", "label": "Efectivo en Cajas", "unit": "ARS Mill."},
            4: {"name": "usd_minorista", "label": "USD Minorista", "unit": "ARS"},
            5: {"name": "usd_mayorista", "label": "USD Mayorista", "unit": "ARS"},
            6: {"name": "tasa_politica_nominal", "label": "Tasa Política (nominal)", "unit": "%"},
            7: {"name": "badlar_bancos_privados", "label": "BADLAR Bancos Privados", "unit": "%"},
            8: {"name": "tm20_bancos_privados", "label": "TM20 Bancos Privados", "unit": "%"},
            
            # Tasas de interés específicas
            9: {"name": "call_money_entre_entidades", "label": "Call Money", "unit": "%"},
            10: {"name": "pases_activos_bcra", "label": "Pases Activos BCRA", "unit": "%"},
            11: {"name": "pases_pasivos_bcra", "label": "Pases Pasivos BCRA", "unit": "%"},
            12: {"name": "leliq_stock", "label": "LELIQs Stock", "unit": "ARS Mill."},
            13: {"name": "nobac_stock", "label": "NOBACs Stock", "unit": "ARS Mill."},
            14: {"name": "lebac_stock", "label": "LEBACs Stock", "unit": "ARS Mill."},
            15: {"name": "base_monetaria", "label": "Base Monetaria", "unit": "ARS Mill."},
            
            # Depósitos y préstamos
            16: {"name": "depositos_dolares", "label": "Depósitos en USD", "unit": "USD Mill."},
            17: {"name": "prestamos_dolares", "label": "Préstamos en USD", "unit": "USD Mill."},
            18: {"name": "depositos_sector_privado", "label": "Depósitos Sector Privado", "unit": "ARS Mill."},
            19: {"name": "prestamos_sector_privado", "label": "Préstamos Sector Privado", "unit": "ARS Mill."},
            20: {"name": "m2_amplio", "label": "M2 Amplio", "unit": "ARS Mill."},
            21: {"name": "depositos_total", "label": "Depósitos Totales", "unit": "ARS Mill."},
            22: {"name": "cuentas_corrientes", "label": "Cuentas Corrientes", "unit": "ARS Mill."},
            23: {"name": "cajas_ahorro", "label": "Cajas de Ahorro", "unit": "ARS Mill."},
            24: {"name": "plazo_fijo", "label": "Plazos Fijos", "unit": "ARS Mill."},
            
            # Inflación y precios
            25: {"name": "cpi_nivel_general", "label": "CPI Nivel General", "unit": "Base 2016=100"},
            26: {"name": "cpi_alimentos_bebidas", "label": "CPI Alimentos y Bebidas", "unit": "Base 2016=100"},
            27: {"name": "inflacion_mensual", "label": "Inflación Mensual", "unit": "%"},
            28: {"name": "inflacion_interanual", "label": "Inflación Interanual", "unit": "%"},
            
            # Tasas específicas por plazo
            29: {"name": "tasa_depositos_30_dias", "label": "Tasa Depósitos 30 días", "unit": "%"},
            30: {"name": "tasa_depositos_60_dias", "label": "Tasa Depósitos 60 días", "unit": "%"},
            31: {"name": "tasa_depositos_90_dias", "label": "Tasa Depósitos 90 días", "unit": "%"},
            32: {"name": "tasa_prestamos_personales", "label": "Tasa Préstamos Personales", "unit": "%"},
            33: {"name": "tasa_prestamos_hipotecarios", "label": "Tasa Préstamos Hipotecarios", "unit": "%"},
            34: {"name": "tasa_politica_efectiva", "label": "Tasa Política (efectiva)", "unit": "%"},
            
            # Sector externo
            35: {"name": "exportaciones", "label": "Exportaciones", "unit": "USD Mill."},
            36: {"name": "importaciones", "label": "Importaciones", "unit": "USD Mill."},
            37: {"name": "balanza_comercial", "label": "Balanza Comercial", "unit": "USD Mill."},
            38: {"name": "cuenta_corriente", "label": "Cuenta Corriente", "unit": "USD Mill."},
            39: {"name": "cuenta_capital", "label": "Cuenta Capital", "unit": "USD Mill."},
            40: {"name": "inversion_extranjera_directa", "label": "Inversión Extranjera Directa", "unit": "USD Mill."},
            
            # Variables adicionales importantes
            41: {"name": "creditos_total", "label": "Créditos Totales", "unit": "ARS Mill."},
            42: {"name": "creditos_consumo", "label": "Créditos al Consumo", "unit": "ARS Mill."},
            43: {"name": "creditos_vivienda", "label": "Créditos para Vivienda", "unit": "ARS Mill."},
            44: {"name": "creditos_comerciales", "label": "Créditos Comerciales", "unit": "ARS Mill."},
            45: {"name": "financiamiento_bcra", "label": "Financiamiento del BCRA", "unit": "ARS Mill."},
        }
        
        # TODAS las monedas disponibles en BCRA (40+)
        self.monedas_completas = [
            # Principales
            "USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD",
            # Regionales
            "BRL", "MXN", "CLP", "COP", "PEN", "UYU", "PYG", "BOB", "VEF",
            # Asiáticas
            "CNY", "KRW", "HKD", "SGD", "INR", "THB", "MYR", "IDR", "PHP",
            # Europeas
            "NOK", "SEK", "DKK", "PLN", "CZK", "HUF", "RON", "BGN",
            # Medio Oriente y África
            "ILS", "AED", "SAR", "ZAR", "EGP", "TRY",
            # Otras importantes
            "RUB", "UAH"
        ]

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_all_bcra_variables(self) -> Dict[str, Any]:
        """Obtener TODAS las variables monetarias disponibles del BCRA"""
        try:
            url = self.base_urls["monetarias"]
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Procesar TODAS las variables
                    variables_procesadas = {}
                    variables_raw = data.get("results", [])
                    
                    logger.info(f"📊 Total variables disponibles en BCRA: {len(variables_raw)}")
                    
                    for item in variables_raw:
                        var_id = item.get("idVariable")
                        
                        # Usar nuestro mapeo si existe, sino crear uno genérico
                        if var_id in self.variables_completas:
                            var_config = self.variables_completas[var_id]
                            key = var_config["name"]
                            label = var_config["label"]
                            unit = var_config["unit"]
                        else:
                            # Para variables no mapeadas, crear nombres genéricos
                            key = f"variable_{var_id}"
                            label = item.get("descripcion", f"Variable {var_id}")
                            unit = self._extract_unit_from_description(item.get("descripcion", ""))
                        
                        variables_procesadas[key] = {
                            "id": var_id,
                            "value": item.get("valor"),
                            "label": label,
                            "unit": unit,
                            "description": item.get("descripcion"),
                            "date": item.get("fecha"),
                            "category": item.get("categoria", "general")
                        }
                    
                    return {
                        "status": "success",
                        "variables": variables_procesadas,
                        "total_variables": len(variables_procesadas),
                        "mapped_variables": len([v for v in variables_procesadas if not v.startswith("variable_")]),
                        "timestamp": datetime.now().isoformat(),
                        "source": "BCRA_EXPANDED"
                    }
                else:
                    logger.error(f"Error BCRA variables: HTTP {response.status}")
                    return {"status": "error", "code": response.status}
                    
        except Exception as e:
            logger.error(f"Error fetching all BCRA variables: {e}")
            return {"status": "error", "message": str(e)}

    async def get_all_cotizaciones(self) -> Dict[str, Any]:
        """Obtener TODAS las cotizaciones disponibles del BCRA"""
        try:
            url = self.base_urls["cotizaciones"]
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Procesar TODAS las cotizaciones
                    cotizaciones = {}
                    detalle = data.get("results", {}).get("detalle", [])
                    
                    logger.info(f"💱 Total cotizaciones disponibles: {len(detalle)}")
                    
                    for item in detalle:
                        codigo = item.get("codigoMoneda")
                        cotizacion = item.get("tipoCotizacion", 0)
                        tipo_pase = item.get("tipoPase", 0)
                        
                        if codigo and cotizacion > 0:
                            cotizaciones[codigo] = {
                                "code": codigo,
                                "rate": cotizacion,
                                "name": item.get("descripcion", codigo),
                                "type_pase": tipo_pase,
                                "category": self._categorize_currency(codigo),
                                "is_major": codigo in ["USD", "EUR", "GBP", "JPY", "CHF"]
                            }
                    
                    return {
                        "status": "success",
                        "date": data.get("results", {}).get("fecha"),
                        "cotizaciones": cotizaciones,
                        "total_currencies": len(cotizaciones),
                        "major_currencies": len([c for c in cotizaciones.values() if c["is_major"]]),
                        "timestamp": datetime.now().isoformat(),
                        "source": "BCRA_EXPANDED"
                    }
                else:
                    logger.error(f"Error BCRA cotizaciones: HTTP {response.status}")
                    return {"status": "error", "code": response.status}
                    
        except Exception as e:
            logger.error(f"Error fetching all BCRA cotizaciones: {e}")
            return {"status": "error", "message": str(e)}

    async def get_complete_dashboard(self) -> Dict[str, Any]:
        """Dashboard COMPLETO con todos los datos disponibles del BCRA"""
        try:
            # Ejecutar consultas en paralelo para máxima velocidad
            tasks = [
                self.get_all_bcra_variables(),
                self.get_all_cotizaciones()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            variables = results[0] if not isinstance(results[0], Exception) else {}
            cotizaciones = results[1] if not isinstance(results[1], Exception) else {}
            
            # Crear dashboard expandido
            dashboard = {
                "summary": {
                    "total_indicators": 0,
                    "total_currencies": 0,
                    "data_sources": ["BCRA_OFICIAL", "TIEMPO_REAL"],
                    "last_update": datetime.now().isoformat()
                },
                "monetary_indicators": {},
                "interest_rates": {},
                "exchange_rates": {},
                "deposits_loans": {},
                "external_sector": {},
                "inflation_data": {},
                "all_currencies": {},
                "status": "success"
            }
            
            # Procesar variables monetarias por categorías
            if variables.get("status") == "success":
                vars_data = variables.get("variables", {})
                dashboard["summary"]["total_indicators"] = len(vars_data)
                
                for key, data in vars_data.items():
                    indicator = {
                        "value": data["value"],
                        "label": data["label"],
                        "unit": data["unit"],
                        "source": "BCRA",
                        "updated": data["date"],
                        "category": data["category"]
                    }
                    
                    # Categorizar por tipo de indicador
                    if any(x in key for x in ["usd", "reservas", "base_monetaria"]):
                        dashboard["monetary_indicators"][key] = indicator
                    elif any(x in key for x in ["tasa", "badlar", "tm20"]):
                        dashboard["interest_rates"][key] = indicator
                    elif any(x in key for x in ["depositos", "prestamos", "creditos"]):
                        dashboard["deposits_loans"][key] = indicator
                    elif any(x in key for x in ["exportaciones", "importaciones", "balanza"]):
                        dashboard["external_sector"][key] = indicator
                    elif any(x in key for x in ["inflacion", "cpi"]):
                        dashboard["inflation_data"][key] = indicator
                    else:
                        dashboard["monetary_indicators"][key] = indicator
            
            # Procesar cotizaciones
            if cotizaciones.get("status") == "success":
                cotiz_data = cotizaciones.get("cotizaciones", {})
                dashboard["summary"]["total_currencies"] = len(cotiz_data)
                
                # Separar principales de todas
                for moneda, data in cotiz_data.items():
                    currency_info = {
                        "rate": data["rate"],
                        "name": data["name"],
                        "category": data["category"],
                        "is_major": data["is_major"],
                        "source": "BCRA",
                        "updated": cotizaciones.get("date")
                    }
                    
                    if data["is_major"]:
                        dashboard["exchange_rates"][moneda] = currency_info
                    
                    dashboard["all_currencies"][moneda] = currency_info
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creating complete dashboard: {e}")
            return {"status": "error", "message": str(e)}

    def _extract_unit_from_description(self, description: str) -> str:
        """Extraer unidad de medida de la descripción"""
        if not description:
            return ""
        
        desc_lower = description.lower()
        
        if "millones" in desc_lower and "usd" in desc_lower:
            return "USD Mill."
        elif "millones" in desc_lower:
            return "ARS Mill."
        elif "%" in description or "tasa" in desc_lower or "porcentual" in desc_lower:
            return "%"
        elif "tipo de cambio" in desc_lower or "cotización" in desc_lower:
            return "ARS"
        elif "índice" in desc_lower or "indice" in desc_lower:
            return "Índice"
        else:
            return ""

    def _categorize_currency(self, currency_code: str) -> str:
        """Categorizar monedas por región/tipo"""
        categories = {
            "major": ["USD", "EUR", "GBP", "JPY", "CHF"],
            "regional": ["BRL", "MXN", "CLP", "COP", "PEN", "UYU"],
            "asian": ["CNY", "KRW", "HKD", "SGD", "INR", "THB"],
            "european": ["NOK", "SEK", "DKK", "PLN", "CZK", "HUF"],
            "emerging": ["TRY", "ZAR", "RUB", "AED", "SAR"]
        }
        
        for category, currencies in categories.items():
            if currency_code in currencies:
                return category
        
        return "other"

    async def save_expanded_data(self, dashboard_data: Dict) -> bool:
        """Guardar todos los datos expandidos en la base de datos"""
        try:
            db = next(get_db())
            saved_count = 0
            
            # Guardar por categorías
            categories = [
                "monetary_indicators", "interest_rates", "exchange_rates",
                "deposits_loans", "external_sector", "inflation_data"
            ]
            
            for category in categories:
                for key, data in dashboard_data.get(category, {}).items():
                    if data.get("value") is not None:
                        indicator = EconomicIndicator(
                            indicator_type=key,
                            value=float(data["value"]),
                            source="BCRA_EXPANDED",
                            date=datetime.now(),
                            is_active=True,
                            metadata_info=json.dumps({
                                "label": data.get("label"),
                                "unit": data.get("unit"),
                                "category": category
                            })
                        )
                        db.add(indicator)
                        saved_count += 1
            
            # Guardar cotizaciones principales
            for key, data in dashboard_data.get("exchange_rates", {}).items():
                if data.get("rate") is not None:
                    indicator = EconomicIndicator(
                        indicator_type=f"exchange_{key.lower()}",
                        value=float(data["rate"]),
                        source="BCRA_EXPANDED",
                        date=datetime.now(),
                        is_active=True,
                        metadata_info=json.dumps({
                            "currency_name": data.get("name"),
                            "category": data.get("category"),
                            "is_major": data.get("is_major")
                        })
                    )
                    db.add(indicator)
                    saved_count += 1
            
            db.commit()
            logger.info(f"✅ Guardados {saved_count} indicadores expandidos en BD")
            return True
            
        except Exception as e:
            logger.error(f"Error saving expanded data: {e}")
            db.rollback()
            return False
        finally:
            db.close()

# Función de test expandida
async def test_bcra_expanded():
    """Test completo del servicio expandido"""
    async with BCRAExpandedService() as service:
        print("🚀 Testing BCRA Expanded Service...")
        print("="*60)
        
        # Test 1: Todas las variables
        print("\n📊 Testing ALL BCRA Variables...")
        variables = await service.get_all_bcra_variables()
        if variables.get("status") == "success":
            total = variables.get("total_variables", 0)
            mapped = variables.get("mapped_variables", 0)
            print(f"✅ Total variables obtenidas: {total}")
            print(f"✅ Variables mapeadas: {mapped}")
            print(f"✅ Variables adicionales: {total - mapped}")
            
            # Mostrar ejemplos de cada categoría
            vars_data = variables.get("variables", {})
            categories = {}
            for key, data in vars_data.items():
                cat = data.get("category", "general")
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(f"{key}: {data['value']} {data['unit']}")
            
            for cat, items in categories.items():
                print(f"\n  📂 {cat.upper()}:")
                for item in items[:3]:  # Mostrar solo 3 ejemplos por categoría
                    print(f"    • {item}")
        else:
            print(f"❌ Error: {variables}")
        
        # Test 2: Todas las cotizaciones
        print("\n💱 Testing ALL Currency Rates...")
        cotizaciones = await service.get_all_cotizaciones()
        if cotizaciones.get("status") == "success":
            total = cotizaciones.get("total_currencies", 0)
            major = cotizaciones.get("major_currencies", 0)
            print(f"✅ Total monedas: {total}")
            print(f"✅ Monedas principales: {major}")
            
            cotiz_data = cotizaciones.get("cotizaciones", {})
            print("\n  💰 Monedas principales:")
            for code, data in cotiz_data.items():
                if data["is_major"]:
                    print(f"    • {code}: {data['rate']} ARS ({data['name']})")
        else:
            print(f"❌ Error: {cotizaciones}")
        
        # Test 3: Dashboard completo
        print("\n🎯 Testing Complete Dashboard...")
        dashboard = await service.get_complete_dashboard()
        if dashboard.get("status") == "success":
            summary = dashboard.get("summary", {})
            print(f"✅ Dashboard completo generado")
            print(f"  • Total indicadores: {summary.get('total_indicators', 0)}")
            print(f"  • Total monedas: {summary.get('total_currencies', 0)}")
            print(f"  • Categorías disponibles:")
            
            categories = ["monetary_indicators", "interest_rates", "exchange_rates", 
                         "deposits_loans", "external_sector", "inflation_data"]
            for cat in categories:
                count = len(dashboard.get(cat, {}))
                print(f"    ▸ {cat.replace('_', ' ').title()}: {count}")
        else:
            print(f"❌ Error: {dashboard}")
        
        print("\n🎉 Test completado! Tu BCRA ahora tiene datos COMPLETOS")

if __name__ == "__main__":
    asyncio.run(test_bcra_expanded())