"""
Sistema de testing comprehensivo para Argfy Platform
Incluye tests de API, performance, integración y E2E
"""

import asyncio
import json
import time
import aiohttp
import requests
from datetime import datetime
from typing import Dict, List, Any
import logging
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArgfyTestSuite:
    """Suite completa de tests para Argfy Platform"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.api_base = f"{backend_url}/api/v1"
        self.test_results = {
            "start_time": datetime.now().isoformat(),
            "backend_url": backend_url,
            "tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        
    async def run_all_tests(self):
        """Ejecutar todos los tests"""
        logger.info("🧪 Iniciando suite completa de tests para Argfy Platform")
        
        test_categories = [
            ("health_tests", "🏥 Health Checks"),
            ("api_functionality_tests", "🔧 API Functionality"),
            ("data_integrity_tests", "📊 Data Integrity"),
            ("performance_tests", "⚡ Performance Tests"),
            ("integration_tests", "🔗 Integration Tests"),
            ("security_tests", "🔒 Security Tests")
        ]
        
        for test_method, description in test_categories:
            logger.info(f"\n{description}")
            logger.info("=" * 50)
            
            try:
                await getattr(self, test_method)()
            except Exception as e:
                logger.error(f"Error in {test_method}: {e}")
                self.record_test(test_method, False, str(e))
        
        self.generate_report()
        return self.test_results
    
    def record_test(self, test_name: str, passed: bool, details: str = "", warning: bool = False):
        """Registrar resultado de un test"""
        self.test_results["tests"][test_name] = {
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "warning": warning
        }
        
        self.test_results["summary"]["total"] += 1
        if passed:
            if warning:
                self.test_results["summary"]["warnings"] += 1
            else:
                self.test_results["summary"]["passed"] += 1
        else:
            self.test_results["summary"]["failed"] += 1

    # HEALTH CHECKS
    async def health_tests(self):
        """Tests de salud del sistema"""
        
        # Test 1: Basic Health Check
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.record_test("basic_health", True, f"Health check OK: {data}")
                    logger.info("✅ Basic health check: PASSED")
                else:
                    self.record_test("basic_health", False, f"Unhealthy status: {data}")
                    logger.error("❌ Basic health check: FAILED")
            else:
                self.record_test("basic_health", False, f"HTTP {response.status_code}")
                logger.error(f"❌ Basic health check: HTTP {response.status_code}")
        except Exception as e:
            self.record_test("basic_health", False, str(e))
            logger.error(f"❌ Basic health check: {e}")
        
        # Test 2: Detailed Health Check
        try:
            response = requests.get(f"{self.backend_url}/health/detailed", timeout=10)
            if response.status_code == 200:
                data = response.json()
                cpu = data.get("system", {}).get("cpu_percent", 0)
                memory = data.get("system", {}).get("memory_percent", 0)
                
                if cpu < 90 and memory < 90:
                    self.record_test("detailed_health", True, f"CPU: {cpu}%, Memory: {memory}%")
                    logger.info(f"✅ Detailed health: CPU {cpu}%, Memory {memory}%")
                else:
                    self.record_test("detailed_health", True, f"High resource usage: CPU {cpu}%, Memory {memory}%", warning=True)
                    logger.warning(f"⚠️ High resource usage: CPU {cpu}%, Memory {memory}%")
            else:
                self.record_test("detailed_health", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.record_test("detailed_health", False, str(e))
    
    # API FUNCTIONALITY TESTS
    async def api_functionality_tests(self):
        """Tests de funcionalidad de la API"""
        
        # Test 1: Root endpoint
        try:
            response = requests.get(self.backend_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "Argfy Platform" in data.get("message", ""):
                    self.record_test("root_endpoint", True, "Root endpoint accessible")
                    logger.info("✅ Root endpoint: PASSED")
                else:
                    self.record_test("root_endpoint", False, f"Unexpected response: {data}")
            else:
                self.record_test("root_endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.record_test("root_endpoint", False, str(e))
        
        # Test 2: Dashboard complete endpoint
        try:
            response = requests.get(f"{self.api_base}/dashboard/complete", timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "data" in data:
                    categories = len(data["data"])
                    total_indicators = data.get("metadata", {}).get("total_indicators", 0)
                    self.record_test("dashboard_complete", True, f"Categories: {categories}, Indicators: {total_indicators}")
                    logger.info(f"✅ Dashboard complete: {categories} categories, {total_indicators} indicators")
                else:
                    self.record_test("dashboard_complete", False, f"Invalid response structure: {data}")
            else:
                self.record_test("dashboard_complete", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.record_test("dashboard_complete", False, str(e))
        
        # Test 3: Category endpoints
        categories = ["economia", "gobierno", "finanzas", "mercados", "tecnologia", "industria"]
        
        for category in categories:
            try:
                response = requests.get(f"{self.api_base}/indicators/{category}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        indicator_count = len([k for k in data["data"].keys() if k not in ["timestamp", "category"]])
                        self.record_test(f"category_{category}", True, f"{indicator_count} indicators")
                        logger.info(f"✅ Category {category}: {indicator_count} indicators")
                    else:
                        self.record_test(f"category_{category}", False, f"Invalid response: {data}")
                else:
                    self.record_test(f"category_{category}", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.record_test(f"category_{category}", False, str(e))
        
        # Test 4: Search functionality
        try:
            response = requests.get(f"{self.api_base}/indicators/search?q=dolar", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    results = len(data.get("results", []))
                    self.record_test("search_functionality", True, f"Search returned {results} results")
                    logger.info(f"✅ Search functionality: {results} results for 'dolar'")
                else:
                    self.record_test("search_functionality", False, f"Search failed: {data}")
            else:
                self.record_test("search_functionality", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.record_test("search_functionality", False, str(e))

    # DATA INTEGRITY TESTS
    async def data_integrity_tests(self):
        """Tests de integridad de datos"""
        
        # Test 1: Data structure validation
        try:
            response = requests.get(f"{self.api_base}/dashboard/complete", timeout=15)
            if response.status_code == 200:
                data = response.json()
                
                # Verificar estructura básica
                required_fields = ["status", "data", "metadata"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.record_test("data_structure", True, "All required fields present")
                    logger.info("✅ Data structure validation: PASSED")
                else:
                    self.record_test("data_structure", False, f"Missing fields: {missing_fields}")
                    logger.error(f"❌ Missing fields: {missing_fields}")
                
                # Verificar que los valores son válidos
                invalid_values = []
                for category, category_data in data.get("data", {}).items():
                    for indicator_id, indicator_data in category_data.items():
                        if indicator_id in ["timestamp", "category"]:
                            continue
                        
                        if "value" not in indicator_data:
                            invalid_values.append(f"{category}.{indicator_id}: missing value")
                        elif indicator_data["value"] is None:
                            invalid_values.append(f"{category}.{indicator_id}: null value")
                
                if not invalid_values:
                    self.record_test("data_values", True, "All indicators have valid values")
                    logger.info("✅ Data values validation: PASSED")
                else:
                    self.record_test("data_values", False, f"Invalid values: {invalid_values[:5]}")  # Mostrar solo primeros 5
                    logger.error(f"❌ Found {len(invalid_values)} invalid values")
                    
        except Exception as e:
            self.record_test("data_structure", False, str(e))
            self.record_test("data_values", False, str(e))
        
        # Test 2: Historical data consistency
        test_indicators = ["dolar_blue", "reservas_bcra", "ipc"]
        
        for indicator in test_indicators:
            try:
                response = requests.get(f"{self.api_base}/indicators/{indicator}/historical?days=7", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        historical_data = data.get("historical_data", [])
                        if len(historical_data) > 0:
                            # Verificar que las fechas están ordenadas
                            dates = [point["date"] for point in historical_data]
                            sorted_dates = sorted(dates)
                            
                            if dates == sorted_dates:
                                self.record_test(f"historical_{indicator}", True, f"{len(historical_data)} data points, dates ordered")
                                logger.info(f"✅ Historical {indicator}: {len(historical_data)} points")
                            else:
                                self.record_test(f"historical_{indicator}", False, "Dates not properly ordered")
                        else:
                            self.record_test(f"historical_{indicator}", True, "No historical data", warning=True)
                            logger.warning(f"⚠️ Historical {indicator}: No data points")
                    else:
                        self.record_test(f"historical_{indicator}", False, f"Failed to get historical data: {data}")
                else:
                    self.record_test(f"historical_{indicator}", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.record_test(f"historical_{indicator}", False, str(e))

    # PERFORMANCE TESTS
    async def performance_tests(self):
        """Tests de performance"""
        
        # Test 1: Response time for main dashboard
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_base}/dashboard/complete", timeout=30)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200 and response_time < 5.0:  # 5 segundos máximo
                self.record_test("dashboard_response_time", True, f"Response time: {response_time:.2f}s")
                logger.info(f"✅ Dashboard response time: {response_time:.2f}s")
            elif response.status_code == 200:
                self.record_test("dashboard_response_time", True, f"Slow response: {response_time:.2f}s", warning=True)
                logger.warning(f"⚠️ Slow dashboard response: {response_time:.2f}s")
            else:
                self.record_test("dashboard_response_time", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.record_test("dashboard_response_time", False, str(e))
        
        # Test 2: Concurrent requests
        async def concurrent_request_test():
            try:
                async with aiohttp.ClientSession() as session:
                    start_time = time.time()
                    
                    # 10 requests concurrentes
                    tasks = []
                    for _ in range(10):
                        tasks.append(session.get(f"{self.api_base}/indicators/economia"))
                    
                    responses = await asyncio.gather(*tasks, return_exceptions=True)
                    end_time = time.time()
                    
                    total_time = end_time - start_time
                    successful = sum(1 for r in responses if not isinstance(r, Exception) and r.status == 200)
                    
                    if successful >= 8:  # Al menos 8 de 10 exitosas
                        self.record_test("concurrent_requests", True, f"{successful}/10 successful in {total_time:.2f}s")
                        logger.info(f"✅ Concurrent requests: {successful}/10 in {total_time:.2f}s")
                    else:
                        self.record_test("concurrent_requests", False, f"Only {successful}/10 successful")
                        logger.error(f"❌ Concurrent requests: only {successful}/10 successful")
                        
            except Exception as e:
                self.record_test("concurrent_requests", False, str(e))
        
        await concurrent_request_test()
        
        # Test 3: Memory usage (estimado por tamaño de respuesta)
        try:
            response = requests.get(f"{self.api_base}/dashboard/complete")
            if response.status_code == 200:
                response_size = len(response.content)
                response_size_mb = response_size / (1024 * 1024)
                
                if response_size_mb < 5:  # Menos de 5MB
                    self.record_test("response_size", True, f"Response size: {response_size_mb:.2f}MB")
                    logger.info(f"✅ Response size: {response_size_mb:.2f}MB")
                else:
                    self.record_test("response_size", True, f"Large response: {response_size_mb:.2f}MB", warning=True)
                    logger.warning(f"⚠️ Large response size: {response_size_mb:.2f}MB")
        except Exception as e:
            self.record_test("response_size", False, str(e))

    # INTEGRATION TESTS
    async def integration_tests(self):
        """Tests de integración entre componentes"""
        
        # Test 1: API documentation accessibility
        try:
            response = requests.get(f"{self.backend_url}/docs", timeout=10)
            if response.status_code == 200:
                self.record_test("api_docs", True, "API documentation accessible")
                logger.info("✅ API documentation: Accessible")
            else:
                self.record_test("api_docs", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.record_test("api_docs", False, str(e))
        
        # Test 2: Configuration endpoint
        try:
            response = requests.get(f"{self.api_base}/config/categories", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "categories" in data and len(data["categories"]) >= 6:
                    self.record_test("config_categories", True, f"{len(data['categories'])} categories configured")
                    logger.info(f"✅ Config categories: {len(data['categories'])} categories")
                else:
                    self.record_test("config_categories", False, f"Invalid config: {data}")
            else:
                self.record_test("config_categories", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.record_test("config_categories", False, str(e))
        
        # Test 3: Stats endpoint
        try:
            response = requests.get(f"{self.api_base}/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                total_indicators = stats.get("total_indicators", 0)
                
                if total_indicators >= 30:  # Al menos 30 indicadores
                    self.record_test("platform_stats", True, f"{total_indicators} total indicators")
                    logger.info(f"✅ Platform stats: {total_indicators} indicators")
                else:
                    self.record_test("platform_stats", True, f"Limited indicators: {total_indicators}", warning=True)
                    logger.warning(f"⚠️ Only {total_indicators} indicators configured")
            else:
                self.record_test("platform_stats", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.record_test("platform_stats", False, str(e))

    # SECURITY TESTS
    async def security_tests(self):
        """Tests básicos de seguridad"""
        
        # Test 1: CORS headers
        try:
            response = requests.options(self.api_base, timeout=5)
            cors_header = response.headers.get("Access-Control-Allow-Origin")
            
            if cors_header:
                self.record_test("cors_configured", True, f"CORS header present: {cors_header}")
                logger.info(f"✅ CORS configured: {cors_header}")
            else:
                self.record_test("cors_configured", False, "No CORS headers found")
                logger.error("❌ No CORS headers configured")
        except Exception as e:
            self.record_test("cors_configured", False, str(e))
        
        # Test 2: Security headers
        try:
            response = requests.get(self.backend_url, timeout=5)
            security_headers = {
                "X-Content-Type-Options": response.headers.get("X-Content-Type-Options"),
                "X-Frame-Options": response.headers.get("X-Frame-Options"),
                "X-XSS-Protection": response.headers.get("X-XSS-Protection")
            }
            
            present_headers = [k for k, v in security_headers.items() if v]
            
            if len(present_headers) >= 2:
                self.record_test("security_headers", True, f"Security headers: {present_headers}")
                logger.info(f"✅ Security headers: {present_headers}")
            else:
                self.record_test("security_headers", True, f"Limited security headers: {present_headers}", warning=True)
                logger.warning(f"⚠️ Limited security headers: {present_headers}")
                
        except Exception as e:
            self.record_test("security_headers", False, str(e))
        
        # Test 3: Invalid endpoint handling
        try:
            response = requests.get(f"{self.api_base}/invalid-endpoint-test", timeout=5)
            if response.status_code == 404:
                self.record_test("invalid_endpoint", True, "404 for invalid endpoints")
                logger.info("✅ Invalid endpoint handling: Returns 404")
            else:
                self.record_test("invalid_endpoint", False, f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.record_test("invalid_endpoint", False, str(e))

    def generate_report(self):
        """Generar reporte final"""
        self.test_results["end_time"] = datetime.now().isoformat()
        
        summary = self.test_results["summary"]
        total = summary["total"]
        passed = summary["passed"]
        failed = summary["failed"]
        warnings = summary["warnings"]
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*60)
        print("🧪 ARGFY PLATFORM TEST REPORT")
        print("="*60)
        print(f"📊 Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print("="*60)
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! Platform ready for deployment.")
        elif failed <= 2:
            print("⚠️ Minor issues found. Platform mostly ready.")
        else:
            print("❌ Multiple failures detected. Platform needs fixes before deployment.")
        
        # Guardar reporte en archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"test_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return success_rate >= 80  # 80% como umbral de éxito


# CLI para ejecutar tests
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Argfy Platform Test Suite')
    parser.add_argument('--backend-url', default='http://localhost:8000', 
                       help='Backend URL to test')
    parser.add_argument('--quick', action='store_true',
                       help='Run only essential tests')
    
    args = parser.parse_args()
    
    tester = ArgfyTestSuite(args.backend_url)
    
    if args.quick:
        # Solo tests esenciales
        await tester.health_tests()
        await tester.api_functionality_tests()
        tester.generate_report()
    else:
        # Suite completa
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
