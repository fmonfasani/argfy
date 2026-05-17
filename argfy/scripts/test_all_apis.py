import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APITester:
    def __init__(self):
        self.session = None
        self.results = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def test_bcra_api(self) -> Dict:
        """Test API oficial del BCRA"""
        endpoints = {
            "principales_variables": "https://api.bcra.gob.ar/estadisticas/v2.0/principalesvariables",
            "usd_oficial": "https://api.bcra.gob.ar/estadisticas/v2.0/datosvariable/1",
            "reservas": "https://api.bcra.gob.ar/estadisticas/v2.0/datosvariable/15",
            "tasa_politica": "https://api.bcra.gob.ar/estadisticas/v2.0/datosvariable/7",
            "base_monetaria": "https://api.bcra.gob.ar/estadisticas/v2.0/datosvariable/25"
        }
        
        results = {}
        for name, url in endpoints.items():
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        results[name] = {
                            "status": "✅ SUCCESS",
                            "data_count": len(data.get("results", [])),
                            "last_value": data.get("results", [])[-1] if data.get("results") else None,
                            "response_time": response.headers.get("x-response-time", "unknown")
                        }
                    else:
                        results[name] = {"status": f"❌ HTTP {response.status}"}
            except Exception as e:
                results[name] = {"status": f"❌ ERROR: {str(e)}"}
                
        return results

    async def test_dolar_blue_apis(self) -> Dict:
        """Test APIs de dólar blue"""
        apis = {
            "bluelytics": "https://api.bluelytics.com.ar/v2/latest",
            "dolarapi": "https://dolarapi.com/v1/dolares/blue",
            "dolarsi": "https://www.dolarsi.com/api/api.php?type=valoresprincipales"
        }
        
        results = {}
        for name, url in apis.items():
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extraer valor según API
                        value = None
                        if name == "bluelytics":
                            value = data.get("blue", {}).get("value_sell")
                        elif name == "dolarapi":
                            value = data.get("venta")
                        elif name == "dolarsi":
                            blue_item = next((item for item in data if "Blue" in item.get("casa", {}).get("nombre", "")), None)
                            if blue_item:
                                value = blue_item.get("casa", {}).get("venta")
                        
                        results[name] = {
                            "status": "✅ SUCCESS",
                            "blue_value": value,
                            "timestamp": datetime.now().isoformat(),
                            "raw_data": data if len(str(data)) < 500 else "truncated"
                        }
                    else:
                        results[name] = {"status": f"❌ HTTP {response.status}"}
            except Exception as e:
                results[name] = {"status": f"❌ ERROR: {str(e)}"}
                
        return results

    async def test_byma_api(self) -> Dict:
        """Test API de BYMA (Bolsa Argentina)"""
        # BYMA requiere registro, por ahora test con endpoints públicos
        endpoints = {
            "merval": "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/index/MERV",
            "general": "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/"
        }
        
        results = {}
        # Por implementar cuando tengamos acceso a BYMA
        results["byma"] = {"status": "⏳ PENDING - Requires registration"}
        return results

    async def test_global_markets(self) -> Dict:
        """Test APIs de mercados globales"""
        # Yahoo Finance (sin key)
        symbols = ["^GSPC", "^IXIC", "^DJI", "^FTSE", "^GDAXI"]  # S&P500, NASDAQ, etc.
        
        results = {}
        for symbol in symbols:
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        chart = data.get("chart", {}).get("result", [{}])[0]
                        meta = chart.get("meta", {})
                        
                        results[symbol] = {
                            "status": "✅ SUCCESS",
                            "current_price": meta.get("regularMarketPrice"),
                            "change": meta.get("regularMarketChangePercent"),
                            "currency": meta.get("currency"),
                            "exchange": meta.get("exchangeName")
                        }
                    else:
                        results[symbol] = {"status": f"❌ HTTP {response.status}"}
            except Exception as e:
                results[symbol] = {"status": f"❌ ERROR: {str(e)}"}
                
        return results

    async def test_forex_apis(self) -> Dict:
        """Test APIs de Forex"""
        # Fixer.io (requiere key para uso real)
        try:
            url = "https://api.fixer.io/v1/latest?access_key=demo&symbols=USD,EUR,GBP,JPY"
            async with self.session.get(url) as response:
                data = await response.json()
                return {
                    "fixer": {
                        "status": "✅ SUCCESS" if data.get("success") else "❌ FAILED",
                        "rates": data.get("rates", {}),
                        "base": data.get("base")
                    }
                }
        except Exception as e:
            return {"fixer": {"status": f"❌ ERROR: {str(e)}"}}

    async def test_indec_api(self) -> Dict:
        """Test API de INDEC (Inflación)"""
        endpoints = {
            "ipc_nacional": "https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELNAL_DICI_M_26&limit=1",
            "emae": "https://apis.datos.gob.ar/series/api/series/?ids=143.3_NO_PR_2004_A_21&limit=1"
        }
        
        results = {}
        for name, url in endpoints.items():
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        series_data = data.get("data", [[]])[0] if data.get("data") else []
                        
                        results[name] = {
                            "status": "✅ SUCCESS",
                            "last_value": series_data[1] if len(series_data) > 1 else None,
                            "last_date": series_data[0] if len(series_data) > 0 else None,
                            "total_points": len(data.get("data", []))
                        }
                    else:
                        results[name] = {"status": f"❌ HTTP {response.status}"}
            except Exception as e:
                results[name] = {"status": f"❌ ERROR: {str(e)}"}
                
        return results

    async def run_all_tests(self) -> Dict:
        """Ejecutar todos los tests"""
        logger.info("🔄 Starting comprehensive API testing...")
        
        # Ejecutar todos los tests en paralelo
        tasks = [
            self.test_bcra_api(),
            self.test_dolar_blue_apis(),
            self.test_byma_api(),
            self.test_global_markets(),
            self.test_forex_apis(),
            self.test_indec_api()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "bcra": results[0],
            "dolar_blue": results[1],
            "byma": results[2],
            "global_markets": results[3],
            "forex": results[4],
            "indec": results[5]
        }

async def main():
    async with APITester() as tester:
        results = await tester.run_all_tests()
        
        # Generar reporte
        print("\n" + "="*60)
        print("🔍 ARGFY API TESTING REPORT")
        print("="*60)
        print(f"⏰ Timestamp: {results['timestamp']}")
        print("\n📊 RESULTS SUMMARY:")
        
        for category, data in results.items():
            if category == "timestamp":
                continue
                
            print(f"\n📁 {category.upper()}:")
            if isinstance(data, dict):
                for api_name, result in data.items():
                    status = result.get("status", "Unknown")
                    print(f"  • {api_name}: {status}")
                    
                    # Mostrar datos adicionales
                    if "blue_value" in result:
                        print(f"    💰 Dólar Blue: ${result['blue_value']}")
                    if "current_price" in result:
                        print(f"    📈 Price: {result['current_price']}")
                    if "last_value" in result:
                        print(f"    📊 Value: {result['last_value']}")
        
        # Guardar reporte detallado
        with open(f"api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n✅ Detailed report saved to api_test_report_*.json")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())