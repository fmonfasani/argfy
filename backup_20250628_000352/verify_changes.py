#!/usr/bin/env python3
# backend/verify_changes.py
# Script para verificar cambios después del instalador híbrido

import os
import sys
from pathlib import Path
import subprocess
from datetime import datetime

def check_file_exists(filepath, description=""):
    """Verificar si un archivo existe y mostrar su tamaño"""
    if Path(filepath).exists():
        size = Path(filepath).stat().st_size
        size_kb = round(size / 1024, 2)
        print(f"✅ {filepath} - {size_kb}KB {description}")
        return True
    else:
        print(f"❌ {filepath} - NO EXISTE {description}")
        return False

def check_dependency(module_name, description=""):
    """Verificar si una dependencia está instalada"""
    try:
        __import__(module_name)
        print(f"✅ {module_name} - DISPONIBLE {description}")
        return True
    except ImportError:
        print(f"❌ {module_name} - NO DISPONIBLE {description}")
        return False

def check_service_import(module_path, description=""):
    """Verificar si un servicio se puede importar"""
    try:
        # Agregar directorio actual al path
        sys.path.insert(0, '.')
        __import__(module_path)
        print(f"✅ {module_path} - IMPORTA OK {description}")
        return True
    except Exception as e:
        print(f"❌ {module_path} - ERROR: {str(e)[:50]}... {description}")
        return False

def main():
    print("🔍 VERIFICACIÓN POST-INSTALACIÓN HÍBRIDA - ARGFY PLATFORM")
    print("="*70)
    print(f"📅 Verificando en: {os.getcwd()}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Contadores
    total_checks = 0
    passed_checks = 0
    
    # 1. VERIFICAR DEPENDENCIAS INSTALADAS
    print("\n📦 VERIFICANDO DEPENDENCIAS INSTALADAS")
    print("-" * 50)
    
    dependencies = [
        ("requests", "HTTP básico + scraping"),
        ("beautifulsoup4", "HTML parsing"),
        ("lxml", "XML/HTML parser rápido"),
        ("httpx", "HTTP moderno async/sync"),
        ("aiohttp", "HTTP async máximo performance"),
        ("schedule", "Task scheduling"),
        ("redis", "Caching"),
    ]
    
    for dep, desc in dependencies:
        total_checks += 1
        if check_dependency(dep, desc):
            passed_checks += 1
    
    # 2. VERIFICAR ESTRUCTURA DE DIRECTORIOS
    print("\n📁 VERIFICANDO ESTRUCTURA DE DIRECTORIOS")
    print("-" * 50)
    
    directories = [
        ("app", "Directorio principal de la app"),
        ("app/services", "Servicios principales"),
        ("app/services/base", "Servicios básicos (requests)"),
        ("app/services/modern", "Servicios modernos (httpx)"),
        ("app/services/performance", "Servicios de performance (aiohttp)"),
        ("app/routers", "Routers de FastAPI"),
    ]
    
    for dir_path, desc in directories:
        total_checks += 1
        if Path(dir_path).is_dir():
            print(f"✅ {dir_path}/ - EXISTE {desc}")
            passed_checks += 1
        else:
            print(f"❌ {dir_path}/ - NO EXISTE {desc}")
    
    # 3. VERIFICAR ARCHIVOS CREADOS
    print("\n📄 VERIFICANDO ARCHIVOS CREADOS")
    print("-" * 50)
    
    files = [
        ("app/services/__init__.py", "Init servicios"),
        ("app/services/http_factory.py", "Factory HTTP inteligente"),
        ("app/services/base/__init__.py", "Init base services"),
        ("app/services/base/scraping_service.py", "Servicio scraping"),
        ("app/services/modern/__init__.py", "Init modern services"),
        ("app/services/modern/bcra_httpx_service.py", "BCRA con httpx"),
        ("app/services/performance/__init__.py", "Init performance services"),
        ("app/services/performance/bcra_massive_service.py", "BCRA masivo"),
        ("app/services/unified_service.py", "Servicio unificado"),
        ("app/services/bcra_scheduler.py", "Scheduler híbrido"),
        ("app/routers/unified_economic.py", "Router unificado"),
        ("requirements.txt", "Dependencias Python"),
    ]
    
    for file_path, desc in files:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # 4. VERIFICAR IMPORTACIONES DE SERVICIOS
    print("\n🧪 VERIFICANDO IMPORTACIONES DE SERVICIOS")
    print("-" * 50)
    
    imports = [
        ("app.services.http_factory", "HTTP Factory"),
        ("app.services.base.scraping_service", "Scraping Service"),
        ("app.services.unified_service", "Unified Service"),
        ("app.services.bcra_scheduler", "Scheduler"),
        ("app.routers.unified_economic", "Router Unificado"),
    ]
    
    for import_path, desc in imports:
        total_checks += 1
        if check_service_import(import_path, desc):
            passed_checks += 1
    
    # 5. VERIFICAR CAPACIDADES HTTP
    print("\n⚡ VERIFICANDO CAPACIDADES HTTP")
    print("-" * 50)
    
    try:
        from app.services.http_factory import HTTPClientFactory
        capabilities = HTTPClientFactory.get_capabilities()
        
        print(f"📊 Capacidades detectadas:")
        for lib, available in capabilities.items():
            status = "✅ DISPONIBLE" if available else "❌ NO DISPONIBLE"
            print(f"  • {lib}: {status}")
            
        # Mostrar recomendaciones
        print(f"\n💡 Recomendaciones:")
        for use_case in ["scraping", "modern_api", "massive_parallel"]:
            client_class, client_type = HTTPClientFactory.get_best_client(use_case)
            print(f"  • {use_case}: {client_type.value}")
            
        total_checks += 1
        passed_checks += 1
        
    except Exception as e:
        print(f"❌ Error verificando capacidades HTTP: {e}")
        total_checks += 1
    
    # 6. VERIFICAR ENDPOINTS DISPONIBLES
    print("\n🌐 VERIFICANDO ENDPOINTS DISPONIBLES")
    print("-" * 50)
    
    try:
        from app.main import app
        
        # Obtener todas las rutas
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        expected_routes = [
            "/",
            "/health", 
            "/api/v1/indicators/current",
            "/api/v1/unified/capabilities",
            "/api/v1/unified/dollar",
            "/api/v1/unified/massive-bcra",
            "/api/v1/unified/test-all"
        ]
        
        for route in expected_routes:
            total_checks += 1
            if route in routes:
                print(f"✅ {route} - DISPONIBLE")
                passed_checks += 1
            else:
                print(f"❌ {route} - NO ENCONTRADO")
        
    except Exception as e:
        print(f"❌ Error verificando endpoints: {e}")
        total_checks += 3  # Estimado
    
    # RESUMEN FINAL
    print("\n" + "="*70)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*70)
    
    success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    print(f"✅ Checks pasados: {passed_checks}/{total_checks}")
    print(f"📈 Tasa de éxito: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 ¡INSTALACIÓN HÍBRIDA COMPLETAMENTE EXITOSA!")
        print("🚀 Tu stack HTTP híbrido está listo para 100+ indicadores económicos")
        print("\n🔧 PRÓXIMOS PASOS:")
        print("1. Agregar router unificado a main.py:")
        print("   from app.routers import unified_economic")
        print("   app.include_router(unified_economic.router)")
        print("2. Iniciar servidor: uvicorn app.main:app --reload")
        print("3. Probar: http://localhost:8000/api/v1/unified/capabilities")
        
    elif success_rate >= 70:
        print("✅ ¡INSTALACIÓN MAYORMENTE EXITOSA!")
        print("⚠️  Algunos componentes opcionales fallaron, pero el core funciona")
        print("🔧 Revisa los errores arriba para optimizar")
        
    elif success_rate >= 50:
        print("⚠️  INSTALACIÓN PARCIAL")
        print("🔧 Funcionalidad básica disponible, pero necesita ajustes")
        
    else:
        print("❌ INSTALACIÓN PROBLEMÁTICA")
        print("🔧 Muchos componentes fallaron, revisar instalación")
    
    print("\n💡 Para test completo del stack:")
    print("   python -c \"from app.services.http_factory import HTTPClientFactory; print(HTTPClientFactory.get_capabilities())\"")
    
    print("="*70)
    return success_rate >= 70

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)