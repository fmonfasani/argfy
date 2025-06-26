# backend/scripts/test_apis.py
"""
Script para testear todas las APIs necesarias para Argfy Platform
Ejecutar: python scripts/test_apis.py
"""

import asyncio
import aiohttp
import requests
from datetime import datetime
import json
import os
import sys
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class APITester:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {'passed': 0, 'failed': 0, 'total': 0}
        }
        
    def log_result(self, api_name: str, success: bool, data: Any = None, error: str = None):
        """Log test result"""
        self.results['tests'][api_name] = {
            'success': success,
            'data': data,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        
        if success:
            self.results['summary']['passed'] += 1
            print(f"✅ {api_name}: SUCCESS")
            if data:
                print(f"   📊 Sample data: {str(data)[:100]}...")
        else:
            self.results['summary']['failed'] += 1
            print(f"❌ {api_name}: FAILED")
            if error:
                print(f"   🔸 Error: {error}")
        
        self.results['summary']['total'] += 1
        print("")

    async def test_bcra_api(self):
        """Test BCRA (Banco Central) API"""
        print("🏦 Testing BCRA API...")
        
        try:
            # Test 1: Principal Variables
            url = "https://api.bcra.gob.ar/estadisticas/v2.0/principalesvariables"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        sample_data = {
                            'total_variables': len(data.get('results', [])),
                            'sample_variable': data['results'][0] if data.get('results') else None
                        }
                        self.log_result('BCRA - Principal Variables', True, sample_data)
                    else:
                        self.log_result('BCRA - Principal Variables', False, error=f"HTTP {response.status}")
            
            # Test 2: USD Official Rate
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            url = f"https://api.bcra.gob.ar/estadisticas/v2.0/datosvariable/1/{start_date}/{end_date}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('results'):
                            latest = data['results'][-1]
                            sample_data = {
                                'latest_usd': latest['valor'],
                                'date': latest['fecha'],
                                'total_records': len(data['results'])
                            }
                            self.log_result('BCRA - USD Official', True, sample_data)
                        else:
                            self.log_result('BCRA - USD Official', False, error="No data returned")
                    else:
                        self.log_result('BCRA - USD Official', False, error=f"HTTP {response.status}")
            
            # Test 3: Reserves
            url = f"https://api.bcra.gob.ar/estadisticas/v2.0/datosvariable/15/{start_date}/{end_date}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('results'):
                            latest = data['results'][-1]
                            sample_data = {
                                'reserves_usd_m': latest['valor'],
                                'date': latest['fecha']
                            }
                            self.log_result('BCRA - Reserves', True, sample_data)
                        else:
                            self.log_result('BCRA - Reserves', False, error="No reserves data")
                    else:
                        self.log_result('BCRA - Reserves', False, error=f"HTTP {response.status}")
                        
        except Exception as e:
            self.log_result('BCRA API', False, error=str(e))

    async def test_dolar_blue_apis(self):
        """Test Dólar Blue APIs"""
        print("💵 Testing Dólar Blue APIs...")
        
        # Test 1: Bluelytics API
        try:
            url = "https://api.bluelytics.com.ar/v2/latest"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        sample_data = {
                            'blue_buy': data.get('blue', {}).get('value_buy'),
                            'blue_sell': data.get('blue', {}).get('value_sell'),
                            'official_buy': data.get('oficial', {}).get('value_buy'),
                            'official_sell': data.get('oficial', {}).get('value_sell'),
                            'last_update': data.get('last_update')
                        }
                        self.log_result('Bluelytics - Dollar Blue', True, sample_data)
                    else:
                        self.log_result('Bluelytics - Dollar Blue', False, error=f"HTTP {response.status}")
        except Exception as e:
            self.log_result('Bluelytics - Dollar Blue', False, error=str(e))
        
        # Test 2: DolarAPI
        try:
            url = "https://dolarapi.com/v1/dolares"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        blue_data = next((item for item in data if item.get('nombre') == 'Blue'), None)
                        sample_data = {
                            'blue_compra': blue_data.get('compra') if blue_data else None,
                            'blue_venta': blue_data.get('venta') if blue_data else None,
                            'total_types': len(data)
                        }
                        self.log_result('DolarAPI - Multiple Rates', True, sample_data)
                    else:
                        self.log_result('DolarAPI - Multiple Rates', False, error=f"HTTP {response.status}")
        except Exception as e:
            self.log_result('DolarAPI - Multiple Rates', False, error=str(e))
        
        # Test 3: DolarSi (backup)
        try:
            url = "https://www.dolarsi.com/api/api.php?type=valoresprincipales"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        blue_data = next((item for item in data if 'Blue' in item.get('casa', {}).get('nombre', '')), None)
                        sample_data = {
                            'blue_compra': blue_data.get('casa', {}).get('compra') if blue_data else None,
                            'blue_venta': blue_data.get('casa', {}).get('venta') if blue_data else None,
                            'total_houses': len(data)
                        }
                        self.log_result('DolarSi - Exchange Houses', True, sample_data)
                    else:
                        self.log_result('DolarSi - Exchange Houses', False, error=f"HTTP {response.status}")
        except Exception as e:
            self.log_result('DolarSi - Exchange Houses', False, error=str(e))

    async def test_indec_api(self):
        """Test INDEC API for inflation data"""
        print("📊 Testing INDEC API...")
        
        try:
            # IPC Nacional (Inflation)
            url = "https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELNAL_DICI_M_26&limit=12"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('data') and len(data['data']) > 0:
                            latest = data['data'][0]
                            sample_data = {
                                'latest_ipc': latest[1],
                                'date': latest[0],
                                'total_records': len(data['data'])
                            }
                            self.log_result('INDEC - IPC Nacional', True, sample_data)
                        else:
                            self.log_result('INDEC - IPC Nacional', False, error="No IPC data returned")
                    else:
                        self.log_result('INDEC - IPC Nacional', False, error=f"HTTP {response.status}")
        except Exception as e:
            self.log_result('INDEC - IPC Nacional', False, error=str(e))

    def test_free_financial_apis(self):
        """Test free financial APIs with API keys"""
        print("🌍 Testing International Financial APIs...")
        
        # Test Alpha Vantage (requires API key)
        alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if alpha_key:
            try:
                url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=ARS&apikey={alpha_key}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'Realtime Currency Exchange Rate' in data:
                        rate_data = data['Realtime Currency Exchange Rate']
                        sample_data = {
                            'exchange_rate': rate_data.get('5. Exchange Rate'),
                            'last_refreshed': rate_data.get('6. Last Refreshed'),
                            'from_currency': rate_data.get('1. From_Currency Code'),
                            'to_currency': rate_data.get('3. To_Currency Code')
                        }
                        self.log_result('Alpha Vantage - USD/ARS', True, sample_data)
                    else:
                        self.log_result('Alpha Vantage - USD/ARS', False, error="Invalid response format")
                else:
                    self.log_result('Alpha Vantage - USD/ARS', False, error=f"HTTP {response.status_code}")
            except Exception as e:
                self.log_result('Alpha Vantage - USD/ARS', False, error=str(e))
        else:
            self.log_result('Alpha Vantage - USD/ARS', False, error="No API key found (ALPHA_VANTAGE_API_KEY)")
        
        # Test Fixer.io (requires API key)
        fixer_key = os.getenv('FIXER_API_KEY')
        if fixer_key:
            try:
                url = f"https://api.fixer.io/v1/latest?access_key={fixer_key}&symbols=ARS"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        sample_data = {
                            'eur_to_ars': data.get('rates', {}).get('ARS'),
                            'base': data.get('base'),
                            'date': data.get('date')
                        }
                        self.log_result('Fixer.io - EUR/ARS', True, sample_data)
                    else:
                        self.log_result('Fixer.io - EUR/ARS', False, error=data.get('error', {}).get('info', 'Unknown error'))
                else:
                    self.log_result('Fixer.io - EUR/ARS', False, error=f"HTTP {response.status_code}")
            except Exception as e:
                self.log_result('Fixer.io - EUR/ARS', False, error=str(e))
        else:
            self.log_result('Fixer.io - EUR/ARS', False, error="No API key found (FIXER_API_KEY)")

    def test_local_services(self):
        """Test local services and dependencies"""
        print("🔧 Testing Local Services...")
        
        # Test Redis connection
        try:
            import redis
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            r = redis.from_url(redis_url)
            r.ping()
            r.set('argfy_test', 'ok', ex=60)
            test_value = r.get('argfy_test')
            if test_value == b'ok':
                self.log_result('Redis Cache', True, {'connection': 'OK', 'read_write': 'OK'})
            else:
                self.log_result('Redis Cache', False, error="Read/write test failed")
        except Exception as e:
            self.log_result('Redis Cache', False, error=str(e))
        
        # Test database connection
        try:
            import sqlite3
            db_path = 'data/argentina.db'
            os.makedirs('data', exist_ok=True)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            sample_data = {
                'database_path': db_path,
                'tables_count': len(tables),
                'tables': [table[0] for table in tables]
            }
            self.log_result('SQLite Database', True, sample_data)
        except Exception as e:
            self.log_result('SQLite Database', False, error=str(e))

    async def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Argfy Platform API Tests")
        print("=" * 50)
        
        # Test official Argentine APIs
        await self.test_bcra_api()
        await self.test_dolar_blue_apis()
        await self.test_indec_api()
        
        # Test international APIs
        self.test_free_financial_apis()
        
        # Test local services
        self.test_local_services()
        
        # Print summary
        print("📋 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Passed: {self.results['summary']['passed']}")
        print(f"❌ Failed: {self.results['summary']['failed']}")
        print(f"📊 Total: {self.results['summary']['total']}")
        
        success_rate = (self.results['summary']['passed'] / self.results['summary']['total']) * 100
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Save detailed results
        results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Detailed results saved to: {results_file}")
        
        if success_rate < 70:
            print("\n⚠️  WARNING: Low success rate! Check API keys and internet connection.")
        
        return self.results

async def main():
    """Main test function"""
    tester = APITester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())