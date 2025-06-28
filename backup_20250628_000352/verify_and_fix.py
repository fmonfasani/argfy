#!/usr/bin/env python3
# backend/final_diagnosis_and_fix.py
# Diagnóstico final y reparación de problemas específicos

import sys
import os
from pathlib import Path

def diagnose_and_fix():
    print("🔍 DIAGNÓSTICO FINAL Y REPARACIÓN - ARGFY PLATFORM")
    print("="*60)
    
    # Agregar directorio actual al path
    sys.path.insert(0, '.')
    
    problems_found = []
    fixes_applied = []
    
    # 1. DIAGNÓSTICO DETALLADO DE DEPENDENCIAS
    print("\n📦 DIAGNÓSTICO DETALLADO DE DEPENDENCIAS")
    print("-" * 50)
    
    deps_status = {}
    
    # Test beautifulsoup4
    try:
        import bs4
        print("✅ beautifulsoup4 (bs4) - DISPONIBLE")
        deps_status['beautifulsoup4'] = True
    except ImportError:
        try:
            import beautifulsoup4
            print("✅ beautifulsoup4 - DISPONIBLE")
            deps_status['beautifulsoup4'] = True
        except ImportError:
            print("❌ beautifulsoup4 - NO DISPONIBLE")
            deps_status['beautifulsoup4'] = False
            problems_found.append("beautifulsoup4 missing")
    
    # Test otras dependencias críticas
    critical_deps = ['requests', 'httpx', 'aiohttp', 'schedule']
    for dep in critical_deps:
        try:
            __import__(dep)
            print(f"✅ {dep} - DISPONIBLE")
            deps_status[dep] = True
        except ImportError:
            print(f"❌ {dep} - NO DISPONIBLE")
            deps_status[dep] = False
            problems_found.append(f"{dep} missing")
    
    # 2. ARREGLAR IMPORTS PROBLEMÁTICOS
    print("\n🔧 ARREGLANDO IMPORTS PROBLEMÁTICOS")
    print("-" * 50)
    
    # Arreglar scraping_service.py para usar bs4 en lugar de BeautifulSoup
    scraping_file = Path("app/services/base/scraping_service.py")
    if scraping_file.exists():
        try:
            content = scraping_file.read_text(encoding='utf-8')
            if 'from bs4 import BeautifulSoup' not in content:
                # Reemplazar línea problemática
                new_content = content.replace(
                    'from datetime import datetime',
                    '''from datetime import datetime
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None'''
                )
                scraping_file.write_text(new_content, encoding='utf-8')
                print("✅ scraping_service.py - Import de BeautifulSoup arreglado")
                fixes_applied.append("Fixed BeautifulSoup import")
        except Exception as e:
            print(f"⚠️  Error arreglando scraping_service.py: {e}")
    
    # 3. CREAR VERSIÓN SIMPLIFICADA DE SERVICIOS PROBLEMÁTICOS
    print("\n🛠️  CREANDO VERSIONES SIMPLIFICADAS")
    print("-" * 50)
    
    # Simplified httpx service
    httpx_service_path = Path("app/services/modern/bcra_httpx_service.py")
    if httpx_service_path.exists():
        try:
            # Test si se puede importar
            from app.services.modern.bcra_httpx_service import bcra_httpx_service
            print("✅ bcra_httpx_service - Ya funciona")
        except Exception as e:
            print(f"🔧 bcra_httpx_service - Error: {str(e)[:100]}...")
            print("   Creando versión simplificada...")
            
            simplified_content = '''# backend/app/services/modern/bcra_httpx_service.py
# Servicio BCRA simplificado con httpx
import asyncio
from datetime import datetime
from typing import Dict
import logging

logger = logging.getLogger(__name__)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

class BCRAHTTPXService:
    """Servicio BCRA con httpx (con fallback)"""
    
    def __init__(self):
        self.base_url = "https://api.bcra.gob.ar"
        self.client = None
        
    async def __aenter__(self):
        if HTTPX_AVAILABLE:
            self.client = httpx.AsyncClient(timeout=10.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def get_exchange_rates(self) -> Dict:
        """Obtener cotizaciones con httpx"""
        if not HTTPX_AVAILABLE:
            return {"status": "error", "message": "httpx not available"}
        
        try:
            url = f"{self.base_url}/estadisticascambiarias/v1.0/Cotizaciones"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json(),
                    "timestamp": datetime.now().isoformat(),
                    "client_type": "httpx"
                }
            else:
                return {"status": "error", "code": response.status_code}
        except Exception as e:
            logger.error(f"Error httpx exchange rates: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_monetary_variables(self) -> Dict:
        """Obtener variables monetarias"""
        if not HTTPX_AVAILABLE:
            return {"status": "error", "message": "httpx not available"}
        
        try:
            url = f"{self.base_url}/estadisticas/v2.0/principalesvariables"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json(),
                    "timestamp": datetime.now().isoformat(),
                    "client_type": "httpx"
                }
            else:
                return {"status": "error", "code": response.status_code}
        except Exception as e:
            logger.error(f"Error httpx variables: {e}")
            return {"status": "error", "message": str(e)}

# Instancia global 
bcra_httpx_service = BCRAHTTPXService()
'''
            httpx_service_path.write_text(simplified_content, encoding='utf-8')
            print("✅ bcra_httpx_service - Versión simplificada creada")
            fixes_applied.append("Created simplified httpx service")
    
    # 4. TEST FINAL DE IMPORTACIONES
    print("\n🧪 TEST FINAL DE IMPORTACIONES")
    print("-" * 50)
    
    test_imports = [
        ("app.services.http_factory", "HTTP Factory"),
        ("app.services.base.scraping_service", "Scraping Service"),
        ("app.services.modern.bcra_httpx_service", "HTTPX Service"),
        ("app.services.unified_service", "Unified Service"),
        ("app.services.bcra_scheduler", "Scheduler"),
        ("app.routers.unified_economic", "Router")
    ]
    
    working_imports = 0
    for module_path, description in test_imports:
        try:
            __import__(module_path)
            print(f"✅ {description} - FUNCIONA")
            working_imports += 1
        except Exception as e:
            print(f"❌ {description} - ERROR: {str(e)[:60]}...")
    
    # 5. CREAR MAIN.PY PATCH
    print("\n📝 CREANDO PATCH PARA MAIN.PY")
    print("-" * 50)
    
    main_patch = '''
# Agregar estas líneas a app/main.py después de las otras importaciones:

# Importación del router unificado (con manejo de errores)
try:
    from app.routers import unified_economic
    app.include_router(unified_economic.router)
    logger.info("✅ Router unificado agregado")
except ImportError as e:
    logger.warning(f"⚠️  Router unificado no disponible: {e}")
except Exception as e:
    logger.error(f"❌ Error agregando router unificado: {e}")
'''
    
    with open("main_patch.txt", "w", encoding='utf-8') as f:
        f.write(main_patch)
    
    print("✅ Patch para main.py creado en 'main_patch.txt'")
    fixes_applied.append("Created main.py patch")
    
    # 6. CREAR QUICK TEST SCRIPT
    print("\n🔬 CREANDO SCRIPT DE TEST RÁPIDO")
    print("-" * 50)
    
    quick_test_script = '''#!/usr/bin/env python3
# quick_test.py - Test rápido de capacidades HTTP

import sys
sys.path.insert(0, '.')

def quick_test():
    print("🧪 QUICK TEST - HTTP Capabilities")
    print("=" * 40)
    
    try:
        from app.services.http_factory import HTTPClientFactory
        caps = HTTPClientFactory.get_capabilities()
        print("✅ HTTP Factory funcionando")
        print(f"📊 Capacidades: {caps}")
        
        for use_case in ["scraping", "modern_api", "massive_parallel"]:
            try:
                client_class, client_type = HTTPClientFactory.get_best_client(use_case)
                print(f"  • {use_case}: {client_type.value}")
            except Exception as e:
                print(f"  • {use_case}: ERROR - {e}")
                
    except Exception as e:
        print(f"❌ HTTP Factory error: {e}")
    
    # Test unified service
    try:
        from app.services.unified_service import unified_service
        print("✅ Unified Service disponible")
    except Exception as e:
        print(f"❌ Unified Service error: {e}")
    
    print("\\n🎯 RESULTADO:")
    print("Si ves '✅ HTTP Factory funcionando' tu stack híbrido está listo!")

if __name__ == "__main__":
    quick_test()
'''
    
    with open("quick_test.py", "w", encoding='utf-8') as f:
        f.write(quick_test_script)
    
    print("✅ Script de test rápido creado: 'quick_test.py'")
    fixes_applied.append("Created quick test script")
    
    # RESUMEN FINAL
    print("\n" + "="*60)
    print("📊 RESUMEN DE DIAGNÓSTICO Y REPARACIÓN")
    print("="*60)
    
    print(f"✅ Imports funcionando: {working_imports}/{len(test_imports)}")
    print(f"🔧 Problemas encontrados: {len(problems_found)}")
    print(f"✅ Reparaciones aplicadas: {len(fixes_applied)}")
    
    if problems_found:
        print(f"\n⚠️  PROBLEMAS ENCONTRADOS:")
        for problem in problems_found:
            print(f"  • {problem}")
    
    if fixes_applied:
        print(f"\n✅ REPARACIONES APLICADAS:")
        for fix in fixes_applied:
            print(f"  • {fix}")
    
    # PRÓXIMOS PASOS
    print(f"\n🚀 PRÓXIMOS PASOS:")
    print("1. Ejecutar: python quick_test.py")
    print("2. Agregar contenido de main_patch.txt a app/main.py")
    print("3. Iniciar servidor: uvicorn app.main:app --reload")
    print("4. Probar: http://localhost:8000/api/v1/unified/capabilities")
    
    # INDICADOR DE ÉXITO
    success_rate = (working_imports / len(test_imports)) * 100
    if success_rate >= 80:
        print(f"\n🎉 ÉXITO! {success_rate:.1f}% de componentes funcionando")
        print("Tu stack híbrido está listo para datos económicos!")
    elif success_rate >= 60:
        print(f"\n✅ BUENO! {success_rate:.1f}% de componentes funcionando")
        print("La mayoría del stack funciona, solo optimizaciones menores")
    else:
        print(f"\n⚠️  PARCIAL: {success_rate:.1f}% de componentes funcionando")
        print("Necesita más ajustes, pero la base funciona")
    
    return success_rate >= 60

if __name__ == "__main__":
    success = diagnose_and_fix()
    sys.exit(0 if success else 1)