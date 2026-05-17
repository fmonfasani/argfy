"""
Script para testing de performance
Ejecutar: python scripts/performance_test.py
"""
import asyncio
import aiohttp
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import requests

class PerformanceTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    async def test_endpoint_async(self, session, endpoint, num_requests=100):
        """Test asíncrono de un endpoint"""
        url = f"{self.base_url}{endpoint}"
        response_times = []
        errors = 0
        
        async def make_request():
            try:
                start_time = time.time()
                async with session.get(url) as response:
                    await response.text()
                    return time.time() - start_time, response.status
            except Exception as e:
                return None, str(e)
        
        tasks = [make_request() for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
        
        for response_time, status in results:
            if response_time is not None:
                response_times.append(response_time)
                if status != 200:
                    errors += 1
            else:
                errors += 1
        
        return {
            "endpoint": endpoint,
            "total_requests": num_requests,
            "successful_requests": len(response_times),
            "errors": errors,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "median_response_time": statistics.median(response_times) if response_times else 0,
            "requests_per_second": len(response_times) / sum(response_times) if response_times else 0
        }
    
    async def run_performance_tests(self):
        """Ejecutar tests de performance"""
        endpoints = [
            "/health",
            "/api/v1/indicators/current",
            "/api/v1/indicators/historical/dolar_blue?days=7",
            "/api/v1/indicators/news?limit=3"
        ]
        
        print("🚀 Starting performance tests...")
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.test_endpoint_async(session, endpoint, 50) 
                for endpoint in endpoints
            ]
            results = await asyncio.gather(*tasks)
        
        print("\n📊 Performance Test Results:")
        print("=" * 80)
        
        for result in results:
            print(f"\n🔗 Endpoint: {result['endpoint']}")
            print(f"   Total Requests: {result['total_requests']}")
            print(f"   Successful: {result['successful_requests']}")
            print(f"   Errors: {result['errors']}")
            print(f"   Avg Response Time: {result['avg_response_time']:.3f}s")
            print(f"   Min Response Time: {result['min_response_time']:.3f}s")
            print(f"   Max Response Time: {result['max_response_time']:.3f}s")
            print(f"   Median Response Time: {result['median_response_time']:.3f}s")
            print(f"   Requests/Second: {result['requests_per_second']:.2f}")
            
            # Análisis
            if result['avg_response_time'] < 0.1:
                print(f"   Status: ✅ Excellent")
            elif result['avg_response_time'] < 0.5:
                print(f"   Status: 🟡 Good")
            else:
                print(f"   Status: 🔴 Needs optimization")
        
        return results

if __name__ == "__main__":
    tester = PerformanceTester()
    asyncio.run(tester.run_performance_tests())