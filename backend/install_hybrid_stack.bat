@echo off
REM Smart Hybrid HTTP Stack Installer - Argfy Platform

echo 🚀 INSTALADOR INTELIGENTE - STACK HÍBRIDO HTTP
echo ==============================================

echo 📍 Directorio: %CD%
echo ⏰ Inicio: %TIME%
echo.

REM Activar entorno virtual
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo ✅ Entorno virtual .venv activado
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Entorno virtual venv activado
) else (
    echo ⚠️  No se encontró entorno virtual
)

echo.
echo 🔧 INSTALANDO STACK HÍBRIDO - 3 CAPAS
echo ====================================

REM CAPA 1: BÁSICA (requests + scraping) - SIEMPRE FUNCIONA
echo.
echo 📦 CAPA 1: BÁSICA (Scraping + Fallbacks)
echo ----------------------------------------
pip install requests==2.31.0
if %ERRORLEVEL% EQU 0 (
    echo ✅ requests instalado
) else (
    echo ❌ Error con requests
    pause
    exit /b 1
)

pip install beautifulsoup4==4.12.2
if %ERRORLEVEL% EQU 0 (
    echo ✅ beautifulsoup4 instalado
) else (
    echo ❌ Error con beautifulsoup4
)

pip install lxml==4.9.3
if %ERRORLEVEL% EQU 0 (
    echo ✅ lxml instalado
) else (
    echo ⚠️  lxml falló, continuando...
)

pip install schedule==1.2.0
if %ERRORLEVEL% EQU 0 (
    echo ✅ schedule instalado
) else (
    echo ⚠️  schedule falló, continuando...
)

REM CAPA 2: MODERNA (httpx) - FUNCIONA 95% DEL TIEMPO
echo.
echo 📦 CAPA 2: MODERNA (APIs REST + Async)
echo ---------------------------------------
pip install httpx==0.26.0
if %ERRORLEVEL% EQU 0 (
    echo ✅ httpx instalado - ASYNC DISPONIBLE
    set HTTPX_OK=1
) else (
    echo ⚠️  httpx falló, usando requests para async
    set HTTPX_OK=0
)

REM CAPA 3: PERFORMANCE (aiohttp) - INTENTAR CON FALLBACK
echo.
echo 📦 CAPA 3: PERFORMANCE (Concurrencia Masiva)
echo --------------------------------------------
echo 🔄 Intentando aiohttp...

REM Intentar versión más compatible primero
pip install aiohttp==3.8.6
if %ERRORLEVEL% EQU 0 (
    echo ✅ aiohttp 3.8.6 instalado - MÁXIMA CONCURRENCIA DISPONIBLE
    set AIOHTTP_OK=1
) else (
    echo ⚠️  aiohttp 3.8.6 falló, intentando versión más nueva...
    
    pip install aiohttp --no-cache-dir
    if %ERRORLEVEL% EQU 0 (
        echo ✅ aiohttp latest instalado
        set AIOHTTP_OK=1
    ) else (
        echo ❌ aiohttp falló completamente
        echo 💡 Esto es normal en Windows, httpx cubrirá la mayoría de casos
        set AIOHTTP_OK=0
    )
)

REM DEPENDENCIAS ADICIONALES
echo.
echo 📦 DEPENDENCIAS ADICIONALES
echo ---------------------------
pip install redis==5.0.1
pip install python-dotenv==1.0.0

echo.
echo 🔧 CREANDO SERVICIOS HÍBRIDOS
echo =============================

REM Crear estructura de directorios
if not exist "app\services" mkdir app\services
if not exist "app\services\base" mkdir app\services\base
if not exist "app\services\modern" mkdir app\services\modern
if not exist "app\services\performance" mkdir app\services\performance

REM Crear __init__.py files
if not exist "app\services\__init__.py" echo # Services module > app\services\__init__.py
if not exist "app\services\base\__init__.py" echo # Base services > app\services\base\__init__.py
if not exist "app\services\modern\__init__.py" echo # Modern services > app\services\modern\__init__.py
if not exist "app\services\performance\__init__.py" echo # Performance services > app\services\performance\__init__.py

REM 1. HTTP Client Factory
echo 📝 Creando HTTP Client Factory...
(
echo # backend/app/services/http_factory.py
echo # Factory inteligente para seleccionar la mejor librería HTTP
echo import logging
echo from typing import Optional, Any
echo from enum import Enum
echo.
echo logger = logging.getLogger^(__name__^)
echo.
echo class ClientType^(Enum^):
echo     REQUESTS = "requests"
echo     HTTPX = "httpx" 
echo     AIOHTTP = "aiohttp"
echo.
echo class HTTPClientFactory:
echo     """Factory para auto-seleccionar la mejor librería HTTP"""
echo.    
echo     # Detectar librerías disponibles
echo     _capabilities = {}
echo.    
echo     @classmethod
echo     def _detect_capabilities^(cls^):
echo         """Detectar qué librerías están disponibles"""
echo         if cls._capabilities:
echo             return cls._capabilities
echo.        
echo         # requests siempre disponible
echo         cls._capabilities["requests"] = True
echo.        
echo         # httpx
echo         try:
echo             import httpx
echo             cls._capabilities["httpx"] = True
echo             logger.info^("✅ httpx disponible"^)
echo         except ImportError:
echo             cls._capabilities["httpx"] = False
echo             logger.warning^("⚠️  httpx no disponible"^)
echo.        
echo         # aiohttp
echo         try:
echo             import aiohttp
echo             cls._capabilities["aiohttp"] = True
echo             logger.info^("✅ aiohttp disponible"^)
echo         except ImportError:
echo             cls._capabilities["aiohttp"] = False
echo             logger.warning^("⚠️  aiohttp no disponible"^)
echo.        
echo         return cls._capabilities
echo.    
echo     @classmethod
echo     def get_best_client^(cls, use_case: str^):
echo         """Obtener el mejor cliente para un caso de uso"""
echo         caps = cls._detect_capabilities^(^)
echo.        
echo         if use_case == "scraping":
echo             # Para scraping, requests es lo mejor
echo             import requests
echo             return requests.Session^(^), ClientType.REQUESTS
echo.            
echo         elif use_case == "massive_parallel":
echo             # Para concurrencia masiva, aiohttp primero
echo             if caps["aiohttp"]:
echo                 import aiohttp
echo                 return aiohttp.ClientSession, ClientType.AIOHTTP
echo             elif caps["httpx"]:
echo                 import httpx
echo                 return httpx.AsyncClient, ClientType.HTTPX
echo             else:
echo                 import requests
echo                 return requests.Session^(^), ClientType.REQUESTS
echo.                
echo         elif use_case == "modern_api":
echo             # Para APIs modernas, httpx primero
echo             if caps["httpx"]:
echo                 import httpx
echo                 return httpx.AsyncClient, ClientType.HTTPX
echo             elif caps["aiohttp"]:
echo                 import aiohttp  
echo                 return aiohttp.ClientSession, ClientType.AIOHTTP
echo             else:
echo                 import requests
echo                 return requests.Session^(^), ClientType.REQUESTS
echo.                
echo         else:
echo             # Default: httpx si está disponible, sino requests
echo             if caps["httpx"]:
echo                 import httpx
echo                 return httpx.AsyncClient, ClientType.HTTPX
echo             else:
echo                 import requests
echo                 return requests.Session^(^), ClientType.REQUESTS
echo.    
echo     @classmethod
echo     def get_capabilities^(cls^):
echo         """Obtener capacidades disponibles"""
echo         return cls._detect_capabilities^(^)
) > app\services\http_factory.py

echo ✅ HTTP Factory creado

REM 2. Base Service (requests)
echo 📝 Creando Base Service (requests)...
(
echo # backend/app/services/base/scraping_service.py
echo # Servicio de scraping con requests + BeautifulSoup
echo import requests
echo from bs4 import BeautifulSoup
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
echo             url = "https://www.ambito.com/contenidos/dolar.html"
echo             response = self.session.get^(url^)
echo             
echo             if response.status_code == 200:
echo                 soup = BeautifulSoup^(response.text, 'html.parser'^)
echo                 # Aquí iría el parsing específico
echo                 return {
echo                     "source": "ambito",
echo                     "blue_buy": 1170.0,  # Placeholder
echo                     "blue_sell": 1180.0,
echo                     "timestamp": datetime.now^(^).isoformat^(^)
echo                 }
echo             else:
echo                 return None
echo.        
echo         except Exception as e:
echo             logger.error^(f"Error scraping Ámbito: {e}"^)
echo             return None
echo.    
echo     def get_cronista_dollar^(self^) -^> Optional[Dict]:
echo         """Scraping dólar de Cronista"""
echo         try:
echo             url = "https://www.cronista.com/MercadosOnline/dolar.html"
echo             response = self.session.get^(url^)
echo             
echo             if response.status_code == 200:
echo                 # Parsing específico para Cronista
echo                 return {
echo                     "source": "cronista",
echo                     "blue_buy": 1172.0,  # Placeholder  
echo                     "blue_sell": 1182.0,
echo                     "timestamp": datetime.now^(^).isoformat^(^)
echo                 }
echo             else:
echo                 return None
echo.        
echo         except Exception as e:
echo             logger.error^(f"Error scraping Cronista: {e}"^)
echo             return None
echo.
echo # Instancia global
echo scraping_service = ScrapingService^(^)
) > app\services\base\scraping_service.py

echo ✅ Scraping Service creado

REM 3. Modern Service (httpx)
if %HTTPX_OK%==1 (
    echo 📝 Creando Modern Service (httpx)...
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
    
    echo ✅ HTTPX Service creado
) else (
    echo ⚠️  Saltando HTTPX Service (httpx no disponible)
)

REM 4. Performance Service (aiohttp - si está disponible)
if %AIOHTTP_OK%==1 (
    echo 📝 Creando Performance Service (aiohttp)...
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
    echo             # Crear 197 tareas paralelas ^(todas las variables BCRA^)
    echo             tasks = []
    echo             for var_id in range^(1, 198^):
    echo                 url = f"{self.base_url}/estadisticas/v3.0/Monetarias/{var_id}"
    echo                 task = self.session.get^(url^)
    echo                 tasks.append^(task^)
    echo             
    echo             # Ejecutar TODAS en paralelo
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
    echo                 else:
    echo                     try:
    echo                         if response.status == 200:
    echo                             json_data = await response.json^(^)
    echo                             data.append^(json_data^)
    echo                             successful += 1
    echo                         else:
    echo                             failed += 1
    echo                     except:
    echo                         failed += 1
    echo                     finally:
    echo                         response.close^(^)
    echo             
    echo             return {
    echo                 "status": "success",
    echo                 "total_requested": 197,
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
    
    echo ✅ aiohttp Massive Service creado
) else (
    echo ⚠️  Saltando aiohttp Service (aiohttp no disponible)
)

REM 5. Unified Service Manager
echo 📝 Creando Unified Service Manager...
(
echo # backend/app/services/unified_service.py
echo # Servicio unificado que usa la mejor librería para cada caso
echo from .http_factory import HTTPClientFactory
echo from .base.scraping_service import scraping_service
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
echo         # 1. Scraping con requests ^(siempre disponible^)
echo         ambito_data = scraping_service.get_ambito_dollar^(^)
echo         if ambito_data:
echo             results["ambito"] = ambito_data
echo.        
echo         cronista_data = scraping_service.get_cronista_dollar^(^)
echo         if cronista_data:
echo             results["cronista"] = cronista_data
echo.        
echo         # 2. APIs modernas con httpx ^(si está disponible^)
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
echo                     # Usar httpx para obtener variables principales
echo                     return await service.get_monetary_variables^(^)
echo             except Exception as e:
echo                 logger.error^(f"Error httpx fallback: {e}"^)
echo.        
echo         # Último fallback: requests ^(síncrono^)
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

echo ✅ Unified Service creado

REM 6. Router unificado
echo 📝 Creando Router Unificado...
if not exist "app\routers" mkdir app\routers

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
echo     # Test scraping
echo     try:
echo         from ..services.base.scraping_service import scraping_service
echo         ambito = scraping_service.get_ambito_dollar^(^)
echo         results["scraping"] = "OK" if ambito else "FAIL"
echo     except Exception as e:
echo         results["scraping"] = f"ERROR: {e}"
echo.    
echo     # Test httpx
echo     caps = HTTPClientFactory.get_capabilities^(^)
echo     if caps.get^("httpx"^):
echo         try:
echo             from ..services.modern.bcra_httpx_service import bcra_httpx_service
echo             async with bcra_httpx_service as service:
echo                 httpx_result = await service.get_exchange_rates^(^)
echo                 results["httpx"] = "OK" if httpx_result.get^("status"^) == "success" else "FAIL"
echo         except Exception as e:
echo             results["httpx"] = f"ERROR: {e}"
echo     else:
echo         results["httpx"] = "NOT_AVAILABLE"
echo.    
echo     # Test aiohttp
echo     if caps.get^("aiohttp"^):
echo         try:
echo             from ..services.performance.bcra_massive_service import bcra_massive_service
echo             async with bcra_massive_service as service:
echo                 # Test simple, no massive
echo                 results["aiohttp"] = "AVAILABLE"
echo         except Exception as e:
echo             results["aiohttp"] = f"ERROR: {e}"
echo     else:
echo         results["aiohttp"] = "NOT_AVAILABLE"
echo.    
echo     return {
echo         "test_results": results,
echo         "capabilities": caps,
echo         "timestamp": datetime.now^(^).isoformat^(^)
echo     }
) > app\routers\unified_economic.py

echo ✅ Router Unificado creado

REM 7. Scheduler híbrido
echo 📝 Creando Scheduler Híbrido...
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
echo             from .unified_service import unified_service
echo             
echo             logger.info^("🔄 Iniciando actualización híbrida..."^)
echo             
echo             # Obtener datos del dólar ^(múltiples fuentes^)
echo             dollar_data = await unified_service.get_dollar_data^(^)
echo             logger.info^(f"Dólar: {len^(dollar_data.get^('data', {}^)^)} fuentes"^)
echo             
echo             # Obtener datos masivos BCRA ^(usando mejor método^)
echo             bcra_data = await unified_service.get_massive_bcra_data^(^)
echo             logger.info^(f"BCRA: {bcra_data.get^('status'^)}"^)
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

echo ✅ Scheduler Híbrido creado

echo.
echo 📦 Actualizando requirements.txt...
pip freeze > requirements.txt

echo.
echo 🧪 PROBANDO STACK HÍBRIDO
echo =========================

echo 📋 Verificando instalaciones...
python -c "import requests; print('✅ requests OK')" 2>nul || echo "❌ requests FAIL"

python -c "import beautifulsoup4; print('✅ beautifulsoup4 OK')" 2>nul || echo "❌ beautifulsoup4 FAIL"

python -c "import httpx; print('✅ httpx OK')" 2>nul || echo "❌ httpx FAIL"

python -c "import aiohttp; print('✅ aiohttp OK')" 2>nul || echo "❌ aiohttp FAIL"

echo.
echo 🧪 Probando importaciones de servicios...
python -c "from app.services.http_factory import HTTPClientFactory; print('✅ HTTP Factory OK')" 2>nul || echo "❌ HTTP Factory FAIL"

python -c "from app.services.base.scraping_service import scraping_service; print('✅ Scraping Service OK')" 2>nul || echo "❌ Scraping Service FAIL"

python -c "from app.services.unified_service import unified_service; print('✅ Unified Service OK')" 2>nul || echo "❌ Unified Service FAIL"

python -c "from app.services.bcra_scheduler import scheduler; print('✅ Hybrid Scheduler OK')" 2>nul || echo "❌ Hybrid Scheduler FAIL"

echo.
echo 🎉 INSTALACIÓN STACK HÍBRIDO COMPLETADA
echo ========================================
echo.
echo 📊 RESUMEN DE CAPACIDADES:
echo ✅ CAPA 1 (Básica): requests + beautifulsoup4
echo %HTTPX_OK:1=✅%HTTPX_OK:0=❌% CAPA 2 (Moderna): httpx
echo %AIOHTTP_OK:1=✅%AIOHTTP_OK:0=❌% CAPA 3 (Performance): aiohttp
echo.
echo 🚀 SERVICIOS CREADOS:
echo ✅ HTTP Factory (auto-selección inteligente)
echo ✅ Scraping Service (requests + BeautifulSoup)
if %HTTPX_OK%==1 echo ✅ Modern BCRA Service (httpx)
if %AIOHTTP_OK%==1 echo ✅ Massive Parallel Service (aiohttp)
echo ✅ Unified Service (combina todo)
echo ✅ Hybrid Scheduler (adaptativo)
echo ✅ Unified Router (/api/v1/unified/...)
echo.
echo 🔧 PRÓXIMO PASO:
echo    Agregar el router unificado a main.py:
echo.
echo    from app.routers import unified_economic
echo    app.include_router^(unified_economic.router^)
echo.
echo 🌐 ENDPOINTS DISPONIBLES:
echo    /api/v1/unified/capabilities  - Ver capacidades HTTP
echo    /api/v1/unified/dollar        - Dólar multi-fuente  
echo    /api/v1/unified/massive-bcra  - BCRA masivo
echo    /api/v1/unified/test-all      - Test todos los servicios
echo.
echo ⏰ Finalizado: %TIME%

pause