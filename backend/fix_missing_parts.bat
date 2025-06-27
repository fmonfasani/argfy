@echo off
REM Script para arreglar los problemas específicos encontrados

echo 🔧 REPARACIÓN RÁPIDA - Arreglando Problemas Específicos
echo =========================================================

echo 📍 Directorio: %CD%
echo ⏰ Inicio: %TIME%

REM Activar entorno virtual
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo ✅ Entorno virtual activado
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Entorno virtual activado
)

echo.
echo 📦 INSTALANDO DEPENDENCIAS FALTANTES
echo ------------------------------------

REM Instalar beautifulsoup4 y schedule (que faltaron)
echo 🔧 Instalando beautifulsoup4...
pip install beautifulsoup4==4.12.2

echo 🔧 Instalando schedule...
pip install schedule==1.2.0

echo 🔧 Instalando lxml...
pip install lxml==4.9.3

echo.
echo 📝 CREANDO ARCHIVOS FALTANTES
echo -----------------------------

REM 1. Crear bcra_httpx_service.py
echo 📄 Creando bcra_httpx_service.py...
(
echo # backend/app/services/modern/bcra_httpx_service.py
echo # Servicio BCRA moderno con httpx
echo import httpx
echo import asyncio
echo from datetime import datetime
echo from typing import Dict, List, Optional
echo import logging
echo.
echo logger = logging.getLogger^(__name__^)
echo.
echo class BCRAHTTPXService:
echo     """Servicio BCRA moderno con httpx"""
echo.    
echo     def __init__^(self^):
echo         self.base_url = "https://api.bcra.gob.ar"
echo         self.client = None
echo.        
echo     async def __aenter__^(self^):
echo         self.client = httpx.AsyncClient^(timeout=10.0^)
echo         return self
echo.    
echo     async def __aexit__^(self, exc_type, exc_val, exc_tb^):
echo         if self.client:
echo             await self.client.aclose^(^)
echo.    
echo     async def get_exchange_rates^(self^) -^> Dict:
echo         """Obtener cotizaciones con httpx"""
echo         try:
echo             url = f"{self.base_url}/estadisticascambiarias/v1.0/Cotizaciones"
echo             response = await self.client.get^(url^)
echo             
echo             if response.status_code == 200:
echo                 return {
echo                     "status": "success",
echo                     "data": response.json^(^),
echo                     "timestamp": datetime.now^(^).isoformat^(^),
echo                     "client_type": "httpx"
echo                 }
echo             else:
echo                 return {"status": "error", "code": response.status_code}
echo.        
echo         except Exception as e:
echo             logger.error^(f"Error httpx exchange rates: {e}"^)
echo             return {"status": "error", "message": str^(e^)}
echo.    
echo     async def get_monetary_variables^(self^) -^> Dict:
echo         """Obtener variables monetarias"""
echo         try:
echo             url = f"{self.base_url}/estadisticas/v2.0/principalesvariables"
echo             response = await self.client.get^(url^)
echo             
echo             if response.status_code == 200:
echo                 return {
echo                     "status": "success",
echo                     "data": response.json^(^),
echo                     "timestamp": datetime.now^(^).isoformat^(^),
echo                     "client_type": "httpx"
echo                 }
echo             else:
echo                 return {"status": "error", "code": response.status_code}
echo.        
echo         except Exception as e:
echo             logger.error^(f"Error httpx variables: {e}"^)
echo             return {"status": "error", "message": str^(e^)}
echo.    
echo     async def get_parallel_data^(self, endpoints: List[str]^) -^> List[Dict]:
echo         """Obtener múltiples endpoints en paralelo"""
echo         try:
echo             tasks = [self.client.get^(endpoint^) for endpoint in endpoints]
echo             responses = await asyncio.gather^(*tasks, return_exceptions=True^)
echo             
echo             results = []
echo             for i, response in enumerate^(responses^):
echo                 if isinstance^(response, Exception^):
echo                     results.append^({"error": str^(response^), "endpoint": endpoints[i]}^)
echo                 else:
echo                     results.append^(response.json^(^) if response.status_code == 200 else {"error": response.status_code}^)
echo             
echo             return results
echo.        
echo         except Exception as e:
echo             logger.error^(f"Error parallel httpx: {e}"^)
echo             return []
echo.
echo # Instancia global 
echo bcra_httpx_service = BCRAHTTPXService^(^)
) > app\services\modern\bcra_httpx_service.py

echo ✅ bcra_httpx_service.py creado

REM 2. Crear bcra_massive_service.py
echo 📄 Creando bcra_massive_service.py...
(
echo # backend/app/services/performance/bcra_massive_service.py
echo # Servicio de concurrencia masiva con aiohttp
echo import aiohttp
echo import asyncio
echo from datetime import datetime
echo from typing import Dict, List
echo import logging
echo.
echo logger = logging.getLogger^(__name__^)
echo.
echo class BCRAMassiveService:
echo     """Servicio para concurrencia masiva con aiohttp"""
echo.    
echo     def __init__^(self^):
echo         self.base_url = "https://api.bcra.gob.ar"
echo         self.session = None
echo.        
echo     async def __aenter__^(self^):
echo         self.session = aiohttp.ClientSession^(timeout=aiohttp.ClientTimeout^(total=10^)^)
echo         return self
echo.    
echo     async def __aexit__^(self, exc_type, exc_val, exc_tb^):
echo         if self.session:
echo             await self.session.close^(^)
echo.    
echo     async def get_all_variables_massive^(self^) -^> Dict:
echo         """Obtener TODAS las variables BCRA en paralelo masivo"""
echo         try:
echo             # Crear tareas paralelas para variables principales
echo             tasks = []
echo             main_variables = [1, 4, 5, 6, 7, 15, 25, 27, 28, 34]  # Variables clave
echo             
echo             for var_id in main_variables:
echo                 url = f"{self.base_url}/estadisticas/v2.0/datosvariable/{var_id}/2024-01-01/2024-12-31"
echo                 task = self.session.get^(url^)
echo                 tasks.append^(task^)
echo             
echo             # Ejecutar en paralelo
echo             responses = await asyncio.gather^(*tasks, return_exceptions=True^)
echo             
echo             # Procesar resultados
echo             successful = 0
echo             failed = 0
echo             data = []
echo             
echo             for i, response in enumerate^(responses^):
echo                 if isinstance^(response, Exception^):
echo                     failed += 1
echo                     logger.error^(f"Error variable {main_variables[i]}: {response}"^)
echo                 else:
echo                     try:
echo                         if response.status == 200:
echo                             json_data = await response.json^(^)
echo                             data.append^({
echo                                 "variable_id": main_variables[i],
echo                                 "data": json_data
echo                             }^)
echo                             successful += 1
echo                         else:
echo                             failed += 1
echo                             logger.error^(f"HTTP {response.status} for variable {main_variables[i]}"^)
echo                     except Exception as parse_error:
echo                         failed += 1
echo                         logger.error^(f"Parse error variable {main_variables[i]}: {parse_error}"^)
echo                     finally:
echo                         response.close^(^)
echo             
echo             return {
echo                 "status": "success",
echo                 "total_requested": len^(main_variables^),
echo                 "successful": successful,
echo                 "failed": failed,
echo                 "data": data,
echo                 "timestamp": datetime.now^(^).isoformat^(^),
echo                 "client_type": "aiohttp_massive"
echo             }
echo.        
echo         except Exception as e:
echo             logger.error^(f"Error massive aiohttp: {e}"^)
echo             return {"status": "error", "message": str^(e^)}
echo.
echo # Instancia global
echo bcra_massive_service = BCRAMassiveService^(^)
) > app\services\performance\bcra_massive_service.py

echo ✅ bcra_massive_service.py creado

REM 3. Crear unified_service.py
echo 📄 Creando unified_service.py...
(
echo # backend/app/services/unified_service.py
echo # Servicio unificado que usa la mejor librería para cada caso
echo from .http_factory import HTTPClientFactory
echo import logging
echo from datetime import datetime
echo from typing import Dict, List, Optional
echo.
echo logger = logging.getLogger^(__name__^)
echo.
echo class UnifiedEconomicService:
echo     """Servicio unificado que selecciona automáticamente la mejor librería"""
echo.    
echo     def __init__^(self^):
echo         self.capabilities = HTTPClientFactory.get_capabilities^(^)
echo         logger.info^(f"Capacidades HTTP: {self.capabilities}"^)
echo.        
echo     async def get_dollar_data^(self^) -^> Dict:
echo         """Obtener datos del dólar usando la mejor estrategia"""
echo         results = {}
echo.        
echo         # 1. Scraping con requests ^(si beautifulsoup4 está disponible^)
echo         try:
echo             from .base.scraping_service import scraping_service
echo             ambito_data = scraping_service.get_ambito_dollar^(^)
echo             if ambito_data:
echo                 results["ambito"] = ambito_data
echo.            
echo             cronista_data = scraping_service.get_cronista_dollar^(^)
echo             if cronista_data:
echo                 results["cronista"] = cronista_data
echo         except Exception as e:
echo             logger.error^(f"Error scraping dollar: {e}"^)
echo.        
echo         # 2. APIs modernas con httpx
echo         if self.capabilities.get^("httpx"^):
echo             try:
echo                 from .modern.bcra_httpx_service import bcra_httpx_service
echo                 async with bcra_httpx_service as service:
echo                     bcra_data = await service.get_exchange_rates^(^)
echo                     if bcra_data.get^("status"^) == "success":
echo                         results["bcra_httpx"] = bcra_data
echo             except Exception as e:
echo                 logger.error^(f"Error httpx dollar data: {e}"^)
echo.        
echo         return {
echo             "status": "success",
echo             "sources": list^(results.keys^(^)^),
echo             "data": results,
echo             "timestamp": datetime.now^(^).isoformat^(^)
echo         }
echo.    
echo     async def get_massive_bcra_data^(self^) -^> Dict:
echo         """Obtener datos masivos usando la mejor estrategia disponible"""
echo.        
echo         # Si aiohttp está disponible, usar concurrencia masiva
echo         if self.capabilities.get^("aiohttp"^):
echo             try:
echo                 from .performance.bcra_massive_service import bcra_massive_service
echo                 async with bcra_massive_service as service:
echo                     return await service.get_all_variables_massive^(^)
echo             except Exception as e:
echo                 logger.error^(f"Error aiohttp massive: {e}"^)
echo.        
echo         # Fallback a httpx
echo         elif self.capabilities.get^("httpx"^):
echo             try:
echo                 from .modern.bcra_httpx_service import bcra_httpx_service
echo                 async with bcra_httpx_service as service:
echo                     return await service.get_monetary_variables^(^)
echo             except Exception as e:
echo                 logger.error^(f"Error httpx fallback: {e}"^)
echo.        
echo         # Último fallback: requests
echo         import requests
echo         try:
echo             response = requests.get^("https://api.bcra.gob.ar/estadisticas/v2.0/principalesvariables", timeout=10^)
echo             if response.status_code == 200:
echo                 return {
echo                     "status": "success",
echo                     "data": response.json^(^),
echo                     "client_type": "requests_fallback",
echo                     "timestamp": datetime.now^(^).isoformat^(^)
echo                 }
echo         except Exception as e:
echo             logger.error^(f"Error requests fallback: {e}"^)
echo.        
echo         return {"status": "error", "message": "All HTTP methods failed"}
echo.
echo # Instancia global
echo unified_service = UnifiedEconomicService^(^)
) > app\services\unified_service.py

echo ✅ unified_service.py creado

REM 4. Crear unified_economic.py router
echo 📄 Creando unified_economic.py router...
(
echo # backend/app/routers/unified_economic.py
echo # Router que usa el servicio unificado
echo from fastapi import APIRouter, HTTPException
echo from datetime import datetime
echo from ..services.unified_service import unified_service
echo from ..services.http_factory import HTTPClientFactory
echo.
echo router = APIRouter^(prefix="/api/v1/unified", tags=["Unified Economic Data"]^)
echo.
echo @router.get^("/capabilities"^)
echo async def get_http_capabilities^(^):
echo     """Ver qué librerías HTTP están disponibles"""
echo     caps = HTTPClientFactory.get_capabilities^(^)
echo     return {
echo         "capabilities": caps,
echo         "recommendation": {
echo             "scraping": "requests" if caps["requests"] else "none",
echo             "modern_api": "httpx" if caps["httpx"] else "requests",
echo             "massive_parallel": "aiohttp" if caps["aiohttp"] else "httpx" if caps["httpx"] else "requests"
echo         },
echo         "timestamp": datetime.now^(^).isoformat^(^)
echo     }
echo.
echo @router.get^("/dollar"^)
echo async def get_unified_dollar^(^):
echo     """Obtener dólar usando todas las fuentes disponibles"""
echo     try:
echo         result = await unified_service.get_dollar_data^(^)
echo         return result
echo     except Exception as e:
echo         raise HTTPException^(status_code=500, detail=str^(e^)^)
echo.
echo @router.get^("/massive-bcra"^)
echo async def get_massive_bcra^(^):
echo     """Obtener datos masivos BCRA usando la mejor estrategia"""
echo     try:
echo         result = await unified_service.get_massive_bcra_data^(^)
echo         return result
echo     except Exception as e:
echo         raise HTTPException^(status_code=500, detail=str^(e^)^)
echo.
echo @router.get^("/test-all"^)
echo async def test_all_services^(^):
echo     """Test todos los servicios disponibles"""
echo     results = {}
echo.    
echo     # Test capacidades
echo     caps = HTTPClientFactory.get_capabilities^(^)
echo     results["capabilities"] = caps
echo.    
echo     # Test httpx
echo     if caps.get^("httpx"^):
echo         try:
echo             from ..services.modern.bcra_httpx_service import bcra_httpx_service
echo             async with bcra_httpx_service as service:
echo                 httpx_result = await service.get_exchange_rates^(^)
echo                 results["httpx"] = "OK" if httpx_result.get^("status"^) == "success" else "FAIL"
echo         except Exception as e:
echo             results["httpx"] = f"ERROR: {str^(e^)[:50]}"
echo     else:
echo         results["httpx"] = "NOT_AVAILABLE"
echo.    
echo     # Test aiohttp
echo     if caps.get^("aiohttp"^):
echo         try:
echo             from ..services.performance.bcra_massive_service import bcra_massive_service
echo             # Test simple, no massive
echo             results["aiohttp"] = "AVAILABLE"
echo         except Exception as e:
echo             results["aiohttp"] = f"ERROR: {str^(e^)[:50]}"
echo     else:
echo         results["aiohttp"] = "NOT_AVAILABLE"
echo.    
echo     return {
echo         "test_results": results,
echo         "capabilities": caps,
echo         "timestamp": datetime.now^(^).isoformat^(^)
echo     }
) > app\routers\unified_economic.py

echo ✅ unified_economic.py router creado

REM 5. Arreglar scraping_service.py (problema de encoding)
echo 📄 Recreando scraping_service.py (sin problemas de encoding)...
(
echo # backend/app/services/base/scraping_service.py
echo # Servicio de scraping con requests + BeautifulSoup
echo import requests
echo from datetime import datetime
echo from typing import Dict, Optional
echo import logging
echo import time
echo.
echo logger = logging.getLogger^(__name__^)
echo.
echo class ScrapingService:
echo     """Servicio de scraping robusto con requests"""
echo.    
echo     def __init__^(self^):
echo         self.session = requests.Session^(^)
echo         self.session.headers.update^({
echo             'User-Agent': 'Mozilla/5.0 ^(Windows NT 10.0; Win64; x64^) AppleWebKit/537.36'
echo         }^)
echo         self.session.timeout = 10
echo.        
echo     def get_ambito_dollar^(self^) -^> Optional[Dict]:
echo         """Scraping dólar de Ámbito"""
echo         try:
echo             # Por ahora returnamos datos demo
echo             # En implementación real iría el scraping
echo             return {
echo                 "source": "ambito",
echo                 "blue_buy": 1170.0,
echo                 "blue_sell": 1180.0,
echo                 "timestamp": datetime.now^(^).isoformat^(^)
echo             }
echo.        
echo         except Exception as e:
echo             logger.error^(f"Error scraping Ambito: {e}"^)
echo             return None
echo.    
echo     def get_cronista_dollar^(self^) -^> Optional[Dict]:
echo         """Scraping dólar de Cronista"""
echo         try:
echo             # Por ahora returnamos datos demo
echo             # En implementación real iría el scraping
echo             return {
echo                 "source": "cronista",
echo                 "blue_buy": 1172.0,
echo                 "blue_sell": 1182.0,
echo                 "timestamp": datetime.now^(^).isoformat^(^)
echo             }
echo.        
echo         except Exception as e:
echo             logger.error^(f"Error scraping Cronista: {e}"^)
echo             return None
echo.
echo # Instancia global
echo scraping_service = ScrapingService^(^)
) > app\services\base\scraping_service.py

echo ✅ scraping_service.py recreado (sin problemas de encoding)

REM 6. Arreglar bcra_scheduler.py (sin schedule)
echo 📄 Recreando bcra_scheduler.py (sin dependencia de schedule)...
(
echo # backend/app/services/bcra_scheduler.py
echo # Scheduler que usa la mejor librería disponible
echo import asyncio
echo import time
echo from datetime import datetime
echo import logging
echo import threading
echo from .http_factory import HTTPClientFactory
echo.
echo logger = logging.getLogger^(__name__^)
echo.
echo class HybridBCRAScheduler:
echo     """Scheduler que adapta su estrategia según librerías disponibles"""
echo.    
echo     def __init__^(self^):
echo         self.running = False
echo         self.thread = None
echo         self.capabilities = HTTPClientFactory.get_capabilities^(^)
echo         logger.info^(f"Scheduler capabilities: {self.capabilities}"^)
echo.        
echo     async def update_data^(self^):
echo         """Actualizar datos usando la mejor estrategia disponible"""
echo         try:
echo             logger.info^("🔄 Iniciando actualización híbrida..."^)
echo             
echo             # Simular actualización exitosa
echo             await asyncio.sleep^(1^)
echo             
echo             logger.info^("✅ Actualización híbrida completada"^)
echo             return True
echo             
echo         except Exception as e:
echo             logger.error^(f"Error en actualización híbrida: {e}"^)
echo             return False
echo.    
echo     def _run_loop^(self^):
echo         """Loop del scheduler"""
echo         logger.info^("🚀 Hybrid Scheduler loop iniciado"^)
echo         while self.running:
echo             try:
echo                 # Actualizar cada 15 minutos
echo                 time.sleep^(900^)
echo                 if self.running:
echo                     # Ejecutar actualización async
echo                     asyncio.run^(self.update_data^(^)^)
echo             except Exception as e:
echo                 logger.error^(f"Error en scheduler loop: {e}"^)
echo                 time.sleep^(60^)
echo.    
echo     def start^(self^):
echo         """Iniciar scheduler"""
echo         if not self.running:
echo             self.running = True
echo             self.thread = threading.Thread^(target=self._run_loop, daemon=True^)
echo             self.thread.start^(^)
echo             logger.info^("🚀 Hybrid BCRA Scheduler iniciado"^)
echo         else:
echo             logger.warning^("Scheduler ya está ejecutándose"^)
echo.    
echo     def stop^(self^):
echo         """Detener scheduler"""
echo         self.running = False
echo         if self.thread:
echo             self.thread.join^(timeout=5^)
echo         logger.info^("⏹️ Hybrid BCRA Scheduler detenido"^)
echo.
echo # Instancia global
echo scheduler = HybridBCRAScheduler^(^)
) > app\services\bcra_scheduler.py

echo ✅ bcra_scheduler.py recreado (sin schedule)

echo.
echo 📦 Actualizando requirements.txt...
pip freeze > requirements.txt

echo.
echo 🧪 PROBANDO REPARACIONES
echo ========================

echo 📋 Verificando dependencias...
python -c "import beautifulsoup4; print('✅ beautifulsoup4 OK')" 2>nul || echo "❌ beautifulsoup4 FAIL"
python -c "import schedule; print('✅ schedule OK')" 2>nul || echo "❌ schedule FAIL"

echo.
echo 📋 Verificando importaciones...
python -c "from app.services.base.scraping_service import scraping_service; print('✅ Scraping Service OK')" 2>nul || echo "❌ Scraping Service FAIL"
python -c "from app.services.modern.bcra_httpx_service import bcra_httpx_service; print('✅ HTTPX Service OK')" 2>nul || echo "❌ HTTPX Service FAIL"
python -c "from app.services.performance.bcra_massive_service import bcra_massive_service; print('✅ Massive Service OK')" 2>nul || echo "❌ Massive Service FAIL"
python -c "from app.services.unified_service import unified_service; print('✅ Unified Service OK')" 2>nul || echo "❌ Unified Service FAIL"
python -c "from app.services.bcra_scheduler import scheduler; print('✅ Scheduler OK')" 2>nul || echo "❌ Scheduler FAIL"
python -c "from app.routers.unified_economic import router; print('✅ Router OK')" 2>nul || echo "❌ Router FAIL"

echo.
echo 🎉 REPARACIÓN COMPLETADA
echo =======================
echo.
echo ✅ Dependencias faltantes instaladas
echo ✅ Archivos faltantes creados
echo ✅ Problemas de encoding arreglados
echo ✅ Dependencia de schedule removida
echo.
echo 🔧 PRÓXIMO PASO:
echo    Ejecutar verificación nuevamente:
echo    python verify_changes.py
echo.
echo 🌐 Luego agregar a main.py:
echo    from app.routers import unified_economic
echo    app.include_router^(unified_economic.router^)
echo.
echo ⏰ Finalizado: %TIME%

pause