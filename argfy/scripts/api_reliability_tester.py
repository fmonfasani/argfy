# scripts/api_reliability_tester.py
import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import logging
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIReliabilityTester:
    """Sistema completo de testing para APIs económicas argentinas"""
    
    def __init__(self):
        self.session = None
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "apis_tested": 0,
            "apis_working": 0,
            "apis_failed": 0,
            "detailed_results": {},
            "recommendations": []
        }
        
        # Configuración de APIs a testear
        self.apis_config = {
            # BCRA OFICIAL - YA CONFIRMADO FUNCIONANDO
            "bcra_variables": {
                "name": "BCRA Variables Monetarias",
                "url": "https://api.bcra.gob.ar/estadisticas/v3.0/Monetarias",
                "type": "oficial",
                "auth_required": False,
                "expected_fields": ["idVariable", "descripcion", "valor", "fecha"],
                "test_functions": ["test_response_time", "test_data_quality", "test_historical_consistency"]
            },
            "bcra_cotizaciones": {
                "name": "BCRA Cotizaciones",
                "url": "https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones",
                "type": "oficial",
                "auth_required": False,
                "expected_fields": ["codigoMoneda", "tipoCotizacion", "fecha"],
                "test_functions": ["test_response_time", "test_data_quality"]
            },
            
            # SERIES DE TIEMPO - DATOS.GOB.AR
            "series_tiempo_ipc": {
                "name": "Series Tiempo - IPC",
                "url": "https://apis.datos.gob.ar/series/api/series/?ids=143.3_INDEC_PAPERI_IPC_0_0_13&format=json",
                "type": "oficial",
                "auth_required": False,
                "expected_fields": ["data"],
                "test_functions": ["test_response_time", "test_data_format", "test_historical_coverage"]
            },
            "series_tiempo_base_monetaria": {
                "name": "Series Tiempo - Base Monetaria", 
                "url": "https://apis.datos.gob.ar/series/api/series/?ids=sspm_174.1_BaseMonetaria&format=json",
                "type": "oficial",
                "auth_required": False,
                "expected_fields": ["data"],
                "test_functions": ["test_response_time", "test_data_format"]
            },
            "series_tiempo_emae": {
                "name": "Series Tiempo - EMAE",
                "url": "https://apis.datos.gob.ar/series/api/series/?ids=143.3_EMAE_DSM_DC0_0_48&format=json",
                "type": "oficial", 
                "auth_required": False,
                "expected_fields": ["data"],
                "test_functions": ["test_response_time", "test_data_format"]
            },
            
            # MECON - MINISTERIO DE ECONOMÍA
            "mecon_fiscal": {
                "name": "MECON - Resultado Fiscal",
                "url": "https://www.economia.gob.ar/datos/result_fiscal_mensual.csv",
                "type": "oficial",
                "auth_required": False,
                "format": "csv",
                "test_functions": ["test_response_time", "test_csv_format"]
            },
            
            # ARGENTINADATOS - WRAPPER COMUNITARIO
            "argentinadatos_riesgo": {
                "name": "Argentinadatos - Riesgo País",
                "url": "https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais",
                "type": "comunitario",
                "auth_required": False,
                "expected_fields": ["fecha", "valor"],
                "test_functions": ["test_response_time", "test_data_quality", "test_reliability"]
            },
            "argentinadatos_dolar": {
                "name": "Argentinadatos - Dólar Blue",
                "url": "https://api.argentinadatos.com/v1/finanzas/cotizaciones/dolar/blue",
                "type": "comunitario", 
                "auth_required": False,
                "expected_fields": ["fecha", "venta", "compra"],
                "test_functions": ["test_response_time", "test_data_quality"]
            },
            
            # ESTADÍSTICAS BCRA - WRAPPER
            "estadisticasbcra_reservas": {
                "name": "EstadísticasBCRA - Reservas",
                "url": "https://api.estadisticasbcra.com/reservas",
                "type": "wrapper",
                "auth_required": True,
                "note": "Requiere token - testing limitado",
                "test_functions": ["test_response_time", "test_auth_requirement"]
            }
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Argfy-Platform-Testing/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_response_time(self, config: Dict) -> Dict:
        """Test de tiempo de respuesta"""
        times = []
        
        for i in range(3):  # 3 intentos
            start_time = time.time()
            try:
                async with self.session.get(config["url"]) as response:
                    await response.read()
                    times.append(time.time() - start_time)
                    
                await asyncio.sleep(1)  # Pausa entre requests
            except Exception as e:
                times.append(float('inf'))
        
        avg_time = np.mean([t for t in times if t != float('inf')])
        
        return {
            "avg_response_time": avg_time,
            "min_time": min(times),
            "max_time": max([t for t in times if t != float('inf')]) if any(t != float('inf') for t in times) else float('inf'),
            "success_rate": len([t for t in times if t != float('inf')]) / len(times),
            "rating": "excellent" if avg_time < 1 else "good" if avg_time < 3 else "poor"
        }

    async def test_data_quality(self, config: Dict) -> Dict:
        """Test de calidad de datos"""
        try:
            async with self.session.get(config["url"]) as response:
                if response.status != 200:
                    return {"status": "failed", "reason": f"HTTP {response.status}"}
                
                data = await response.json()
                
                # Verificar estructura esperada
                missing_fields = []
                for field in config.get("expected_fields", []):
                    if not self._has_field(data, field):
                        missing_fields.append(field)
                
                # Análisis de datos
                data_points = self._extract_data_points(data, config)
                
                quality_metrics = {
                    "has_expected_fields": len(missing_fields) == 0,
                    "missing_fields": missing_fields,
                    "data_points_count": len(data_points),
                    "has_recent_data": self._has_recent_data(data_points),
                    "data_consistency": self._check_data_consistency(data_points),
                    "rating": "unknown"
                }
                
                # Calcular rating general
                if quality_metrics["has_expected_fields"] and quality_metrics["data_points_count"] > 0:
                    if quality_metrics["has_recent_data"] and quality_metrics["data_consistency"] > 0.8:
                        quality_metrics["rating"] = "excellent"
                    elif quality_metrics["data_points_count"] > 10:
                        quality_metrics["rating"] = "good"
                    else:
                        quality_metrics["rating"] = "fair"
                else:
                    quality_metrics["rating"] = "poor"
                
                return quality_metrics
                
        except Exception as e:
            return {"status": "failed", "reason": str(e)}

    async def test_data_format(self, config: Dict) -> Dict:
        """Test específico para series de tiempo de datos.gob.ar"""
        try:
            async with self.session.get(config["url"]) as response:
                if response.status != 200:
                    return {"status": "failed", "reason": f"HTTP {response.status}"}
                
                data = await response.json()
                
                # Verificar estructura de series de tiempo
                has_data = "data" in data
                has_metadata = "meta" in data
                
                if has_data:
                    data_array = data["data"]
                    sample_point = data_array[0] if data_array else None
                    
                    return {
                        "has_data_field": has_data,
                        "has_metadata": has_metadata,
                        "data_points": len(data_array),
                        "sample_format": type(sample_point).__name__ if sample_point else "empty",
                        "is_time_series": isinstance(sample_point, list) and len(sample_point) == 2,
                        "date_range": self._get_date_range(data_array) if data_array else None,
                        "rating": "excellent" if has_data and len(data_array) > 0 else "poor"
                    }
                else:
                    return {"status": "failed", "reason": "No data field found"}
                    
        except Exception as e:
            return {"status": "failed", "reason": str(e)}

    async def test_csv_format(self, config: Dict) -> Dict:
        """Test para archivos CSV"""
        try:
            async with self.session.get(config["url"]) as response:
                if response.status != 200:
                    return {"status": "failed", "reason": f"HTTP {response.status}"}
                
                content = await response.text()
                
                # Análisis básico del CSV
                lines = content.split('\n')
                headers = lines[0].split(',') if lines else []
                data_rows = len([line for line in lines[1:] if line.strip()])
                
                return {
                    "total_lines": len(lines),
                    "headers": headers[:10],  # Primeros 10 headers
                    "data_rows": data_rows,
                    "file_size_kb": len(content) / 1024,
                    "seems_valid": len(headers) > 1 and data_rows > 0,
                    "rating": "excellent" if data_rows > 100 else "good" if data_rows > 10 else "poor"
                }
                
        except Exception as e:
            return {"status": "failed", "reason": str(e)}

    async def test_reliability(self, config: Dict) -> Dict:
        """Test de confiabilidad - múltiples intentos en el tiempo"""
        results = []
        
        for i in range(5):  # 5 intentos espaciados
            try:
                start_time = time.time()
                async with self.session.get(config["url"]) as response:
                    response_time = time.time() - start_time
                    success = response.status == 200
                    
                    results.append({
                        "attempt": i + 1,
                        "success": success,
                        "response_time": response_time,
                        "status_code": response.status
                    })
                    
                if i < 4:  # No esperar después del último intento
                    await asyncio.sleep(2)
                    
            except Exception as e:
                results.append({
                    "attempt": i + 1,
                    "success": False,
                    "error": str(e)
                })
        
        success_rate = len([r for r in results if r.get("success", False)]) / len(results)
        avg_response_time = np.mean([r.get("response_time", 0) for r in results if r.get("success", False)])
        
        return {
            "attempts": results,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "reliability_score": success_rate * (1 if avg_response_time < 2 else 0.8),
            "rating": "excellent" if success_rate >= 0.9 else "good" if success_rate >= 0.7 else "poor"
        }

    async def test_auth_requirement(self, config: Dict) -> Dict:
        """Test para APIs que requieren autenticación"""
        try:
            async with self.session.get(config["url"]) as response:
                return {
                    "status_without_auth": response.status,
                    "requires_auth": response.status in [401, 403],
                    "accessible": response.status == 200,
                    "response_headers": dict(response.headers),
                    "rating": "needs_setup" if response.status in [401, 403] else "accessible"
                }
        except Exception as e:
            return {"status": "failed", "reason": str(e)}

    async def run_comprehensive_test(self) -> Dict:
        """Ejecutar test completo de todas las APIs"""
        logger.info("🧪 Iniciando testing comprehensivo de APIs...")
        
        for api_key, config in self.apis_config.items():
            logger.info(f"Testing: {config['name']}")
            
            api_result = {
                "name": config["name"],
                "url": config["url"],
                "type": config["type"],
                "auth_required": config.get("auth_required", False),
                "tests_results": {},
                "overall_rating": "unknown",
                "recommendations": []
            }
            
            # Ejecutar tests específicos para esta API
            for test_func_name in config.get("test_functions", []):
                if hasattr(self, test_func_name):
                    test_func = getattr(self, test_func_name)
                    try:
                        result = await test_func(config)
                        api_result["tests_results"][test_func_name] = result
                    except Exception as e:
                        api_result["tests_results"][test_func_name] = {
                            "status": "error",
                            "reason": str(e)
                        }
            
            # Calcular rating general y recomendaciones
            api_result["overall_rating"] = self._calculate_overall_rating(api_result["tests_results"])
            api_result["recommendations"] = self._generate_recommendations(config, api_result["tests_results"])
            
            self.results["detailed_results"][api_key] = api_result
            
            if api_result["overall_rating"] in ["excellent", "good"]:
                self.results["apis_working"] += 1
            else:
                self.results["apis_failed"] += 1
            
            self.results["apis_tested"] += 1
            
            # Pausa entre APIs para no sobrecargar
            await asyncio.sleep(1)
        
        # Generar recomendaciones finales
        self._generate_final_recommendations()
        
        return self.results

    def _has_field(self, data: Any, field: str) -> bool:
        """Verificar si un campo existe en la estructura de datos"""
        if isinstance(data, dict):
            return field in data or any(self._has_field(v, field) for v in data.values() if isinstance(v, (dict, list)))
        elif isinstance(data, list) and data:
            return any(self._has_field(item, field) for item in data[:3])  # Check first 3 items
        return False

    def _extract_data_points(self, data: Any, config: Dict) -> List:
        """Extraer puntos de datos de la respuesta"""
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if "data" in data:
                return data["data"]
            elif "results" in data:
                return data["results"] if isinstance(data["results"], list) else [data["results"]]
        return []

    def _has_recent_data(self, data_points: List) -> bool:
        """Verificar si hay datos recientes (últimos 30 días)"""
        if not data_points:
            return False
        
        recent_threshold = datetime.now() - timedelta(days=30)
        
        for point in data_points[-10:]:  # Check last 10 points
            try:
                if isinstance(point, dict) and "fecha" in point:
                    date_str = point["fecha"]
                elif isinstance(point, list) and len(point) >= 2:
                    date_str = point[0]
                else:
                    continue
                
                # Try different date formats
                for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]:
                    try:
                        date_obj = datetime.strptime(date_str[:len(fmt.replace('%f', '123456'))], fmt)
                        if date_obj > recent_threshold:
                            return True
                        break
                    except ValueError:
                        continue
            except:
                continue
        
        return False

    def _check_data_consistency(self, data_points: List) -> float:
        """Verificar consistencia de datos (% de valores válidos)"""
        if not data_points:
            return 0.0
        
        valid_count = 0
        total_count = len(data_points)
        
        for point in data_points:
            try:
                if isinstance(point, dict):
                    value = point.get("valor") or point.get("value") or point.get("venta")
                elif isinstance(point, list) and len(point) >= 2:
                    value = point[1]
                else:
                    continue
                
                if value is not None and value != "" and str(value).lower() not in ["null", "nan", "none"]:
                    if isinstance(value, (int, float)) or (isinstance(value, str) and value.replace(".", "").isdigit()):
                        valid_count += 1
            except:
                continue
        
        return valid_count / total_count if total_count > 0 else 0.0

    def _get_date_range(self, data_array: List) -> Dict:
        """Obtener rango de fechas de una serie de tiempo"""
        if not data_array:
            return None
        
        try:
            first_date = data_array[0][0] if isinstance(data_array[0], list) else data_array[0].get("fecha")
            last_date = data_array[-1][0] if isinstance(data_array[-1], list) else data_array[-1].get("fecha")
            
            return {
                "from": first_date,
                "to": last_date,
                "total_points": len(data_array)
            }
        except:
            return {"error": "Could not parse date range"}

    def _calculate_overall_rating(self, test_results: Dict) -> str:
        """Calcular rating general basado en todos los tests"""
        ratings = []
        
        for test_name, result in test_results.items():
            if isinstance(result, dict) and "rating" in result:
                ratings.append(result["rating"])
        
        if not ratings:
            return "unknown"
        
        # Conteo de ratings
        excellent_count = ratings.count("excellent")
        good_count = ratings.count("good")
        poor_count = ratings.count("poor")
        
        total = len(ratings)
        
        if excellent_count / total >= 0.7:
            return "excellent"
        elif (excellent_count + good_count) / total >= 0.6:
            return "good" 
        elif poor_count / total >= 0.5:
            return "poor"
        else:
            return "fair"

    def _generate_recommendations(self, config: Dict, test_results: Dict) -> List[str]:
        """Generar recomendaciones específicas para cada API"""
        recommendations = []
        
        # Check response time
        if "test_response_time" in test_results:
            rt_result = test_results["test_response_time"]
            if isinstance(rt_result, dict):
                avg_time = rt_result.get("avg_response_time", 0)
                if avg_time > 3:
                    recommendations.append("⚠️ Respuesta lenta - implementar caché agresivo")
                elif avg_time > 1:
                    recommendations.append("💡 Considerar caché para optimizar performance")
        
        # Check reliability
        if "test_reliability" in test_results:
            rel_result = test_results["test_reliability"]
            if isinstance(rel_result, dict):
                success_rate = rel_result.get("success_rate", 0)
                if success_rate < 0.8:
                    recommendations.append("🚨 Baja confiabilidad - implementar fallbacks")
                elif success_rate < 0.95:
                    recommendations.append("⚠️ Confiabilidad moderada - monitoreo recomendado")
        
        # Check data quality
        if "test_data_quality" in test_results:
            dq_result = test_results["test_data_quality"]
            if isinstance(dq_result, dict):
                if not dq_result.get("has_recent_data", False):
                    recommendations.append("📅 Sin datos recientes - verificar actualización")
                consistency = dq_result.get("data_consistency", 0)
                if consistency < 0.8:
                    recommendations.append("🔍 Baja consistencia - validación de datos necesaria")
        
        # Recomendaciones por tipo
        if config["type"] == "comunitario":
            recommendations.append("🔄 API comunitaria - considerar fuente oficial como backup")
        elif config.get("auth_required"):
            recommendations.append("🔐 Requiere autenticación - configurar tokens")
        
        return recommendations

    def _generate_final_recommendations(self):
        """Generar recomendaciones finales del sistema"""
        working_apis = self.results["apis_working"]
        total_apis = self.results["apis_tested"]
        
        if working_apis / total_apis >= 0.8:
            self.results["recommendations"].append("✅ Excelente cobertura de APIs - proceder con implementación")
        elif working_apis / total_apis >= 0.6:
            self.results["recommendations"].append("⚠️ Cobertura buena - implementar con monitoreo")
        else:
            self.results["recommendations"].append("🚨 Cobertura insuficiente - revisar fuentes alternativas")
        
        # Recomendaciones específicas por tipo
        oficial_count = len([r for r in self.results["detailed_results"].values() 
                           if r["type"] == "oficial" and r["overall_rating"] in ["excellent", "good"]])
        
        if oficial_count >= 3:
            self.results["recommendations"].append("🏛️ Suficientes fuentes oficiales - priorizar estas")
        else:
            self.results["recommendations"].append("⚠️ Pocas fuentes oficiales funcionando - considerar alternativas")

    def generate_report(self) -> str:
        """Generar reporte final en texto"""
        report = []
        report.append("=" * 60)
        report.append("🧪 REPORTE DE CONFIABILIDAD DE APIs ARGENTINAS")
        report.append("=" * 60)
        report.append(f"📊 Resumen: {self.results['apis_working']}/{self.results['apis_tested']} APIs funcionando")
        report.append(f"⏰ Timestamp: {self.results['timestamp']}")
        report.append("")
        
        # APIs por categoría
        for category in ["oficial", "wrapper", "comunitario"]:
            apis_in_category = [r for r in self.results["detailed_results"].values() if r["type"] == category]
            if apis_in_category:
                report.append(f"🏷️ {category.upper()}:")
                for api in apis_in_category:
                    status_emoji = {"excellent": "🟢", "good": "🟡", "fair": "🟠", "poor": "🔴"}.get(api["overall_rating"], "⚪")
                    report.append(f"  {status_emoji} {api['name']}: {api['overall_rating']}")
                    if api["recommendations"]:
                        for rec in api["recommendations"][:2]:  # Max 2 recomendaciones por API
                            report.append(f"    {rec}")
                report.append("")
        
        # Recomendaciones finales
        report.append("🎯 RECOMENDACIONES FINALES:")
        for rec in self.results["recommendations"]:
            report.append(f"  {rec}")
        
        return "\n".join(report)


# Función principal para ejecutar
async def run_api_reliability_test():
    """Ejecutar test completo de confiabilidad"""
    async with APIReliabilityTester() as tester:
        results = await tester.run_comprehensive_test()
        
        # Mostrar reporte
        print(tester.generate_report())
        
        # Guardar resultados detallados
        with open(f"api_reliability_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📁 Reporte detallado guardado en: api_reliability_report_*.json")
        
        return results

if __name__ == "__main__":
    asyncio.run(run_api_reliability_test())