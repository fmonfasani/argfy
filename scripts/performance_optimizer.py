import asyncio
import aiohttp
import time
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Optimizador de performance para Argfy Platform"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.api_base = f"{backend_url}/api/v1"
        
    async def analyze_performance(self):
        """Analizar performance actual"""
        
        print("🔍 ANALIZANDO PERFORMANCE DE ARGFY PLATFORM")
        print("=" * 50)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "recommendations": []
        }
        
        # Test 1: Latencia de endpoints principales
        endpoints = [
            ("/", "Root"),
            ("/health", "Health Check"),
            ("/api/v1/dashboard/complete", "Dashboard Complete"),
            ("/api/v1/indicators/economia", "Category Economia"),
            ("/api/v1/config/categories", "Categories Config")
        ]
        
        print("\n📊 Latencia de Endpoints:")
        for endpoint, name in endpoints:
            latency = await self.measure_endpoint_latency(endpoint)
            results["tests"][f"latency_{endpoint.replace('/', '_')}"] = latency
            
            status = "🟢" if latency < 1.0 else "🟡" if latency < 3.0 else "🔴"
            print(f"{status} {name}: {latency:.2f}s")
            
            if latency > 2.0:
                results["recommendations"].append(f"Optimize {name} endpoint (current: {latency:.2f}s)")
        
        # Test 2: Throughput
        print("\n🚀 Throughput Test:")
        throughput = await self.measure_throughput()
        results["tests"]["throughput"] = throughput
        
        print(f"📈 Requests/second: {throughput:.2f}")
        
        if throughput < 10:
            results["recommendations"].append("Consider adding caching to improve throughput")
        
        # Test 3: Memory usage (simulado)
        print("\n💾 Resource Usage:")
        resource_usage = await self.estimate_resource_usage()
        results["tests"]["resource_usage"] = resource_usage
        
        for resource, value in resource_usage.items():
            print(f"📊 {resource}: {value}")
        
        # Generar recomendaciones
        await self.generate_recommendations(results)
        
        # Guardar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"performance_analysis_{timestamp}.json", "w") as f:
            json.dump(results, f, indent=2)
        
        return results
    
    async def measure_endpoint_latency(self, endpoint: str) -> float:
        """Medir latencia de un endpoint"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}{endpoint}") as response:
                    await response.text()
            
            return time.time() - start_time
        except Exception as e:
            logger.error(f"Error measuring latency for {endpoint}: {e}")
            return 999.0  # Error marker
    
    async def measure_throughput(self) -> float:
        """Medir throughput con requests concurrentes"""
        try:
            concurrent_requests = 20
            test_duration = 10  # segundos
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                completed_requests = 0
                
                while time.time() - start_time < test_duration:
                    # Batch de requests concurrentes
                    tasks = []
                    for _ in range(concurrent_requests):
                        tasks.append(session.get(f"{self.api_base}/health"))
                    
                    responses = await asyncio.gather(*tasks, return_exceptions=True)
                    successful = sum(1 for r in responses if not isinstance(r, Exception))
                    completed_requests += successful
                    
                    # Pequeña pausa para no saturar
                    await asyncio.sleep(0.1)
                
                actual_duration = time.time() - start_time
                return completed_requests / actual_duration
                
        except Exception as e:
            logger.error(f"Error measuring throughput: {e}")
            return 0.0
    
    async def estimate_resource_usage(self) -> dict:
        """Estimar uso de recursos"""
        try:
            async with aiohttp.ClientSession() as session:
                # Hacer request a health detallado
                async with session.get(f"{self.backend_url}/health/detailed") as response:
                    if response.status == 200:
                        data = await response.json()
                        system_info = data.get("system", {})
                        
                        return {
                            "CPU": f"{system_info.get('cpu_percent', 0):.1f}%",
                            "Memory": f"{system_info.get('memory_percent', 0):.1f}%",
                            "Disk": f"{system_info.get('disk_percent', 0):.1f}%"
                        }
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
        
        return {"CPU": "N/A", "Memory": "N/A", "Disk": "N/A"}
    
    async def generate_recommendations(self, results: dict):
        """Generar recomendaciones de optimización"""
        
        print("\n💡 RECOMENDACIONES DE OPTIMIZACIÓN:")
        print("-" * 40)
        
        if not results["recommendations"]:
            results["recommendations"].extend([
                "✅ Performance looks good!",
                "Consider adding response caching for better scalability",
                "Monitor performance under higher load",
                "Implement database connection pooling"
            ])
        
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"{i}. {rec}")
        
        # Recomendaciones adicionales basadas en análisis
        additional_recs = [
            "🔧 Backend Optimizations:",
            "  • Add Redis caching for frequently accessed data",
            "  • Implement database query optimization",
            "  • Use connection pooling for external APIs",
            "  • Add response compression (gzip)",
            "",
            "🎨 Frontend Optimizations:", 
            "  • Implement lazy loading for components",
            "  • Add service worker for caching",
            "  • Optimize bundle size with tree shaking",
            "  • Use React.memo for heavy components",
            "",
            "🚀 Infrastructure:",
            "  • Consider CDN for static assets",
            "  • Implement horizontal scaling",
            "  • Add load balancing",
            "  • Monitor with APM tools"
        ]
        
        print("\n💡 RECOMENDACIONES ADICIONALES:")
        for rec in additional_recs:
            print(rec)