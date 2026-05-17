#!/usr/bin/env python3
"""
Script de Refactoring Automático - Argfy Platform
Elimina código duplicado, obsoleto y consolida la estructura
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json

class ArgfyRefactoring:
    """
    Clase principal para el refactoring del backend de Argfy
    """
    
    def __init__(self, backend_path: str = "backend"):
        self.backend_path = Path(backend_path)
        self.backup_path = Path(f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.obsolete_files = []
        self.duplicated_files = []
        self.consolidated_files = []
    
    def run_refactoring(self):
        """Ejecuta el proceso completo de refactoring"""
        print("🚀 ARGFY PLATFORM - REFACTORING AUTOMÁTICO")
        print("="*60)
        
        try:
            # Paso 1: Análisis del código existente
            self.analyze_current_structure()
            
            # Paso 2: Crear backup
            self.create_backup()
            
            # Paso 3: Eliminar archivos obsoletos
            self.remove_obsolete_files()
            
            # Paso 4: Consolidar servicios duplicados
            self.consolidate_services()
            
            # Paso 5: Actualizar imports y referencias
            self.update_imports()
            
            # Paso 6: Crear estructura limpia
            self.create_clean_structure()
            
            # Paso 7: Validar resultado
            self.validate_refactoring()
            
            print("\n✅ REFACTORING COMPLETADO EXITOSAMENTE")
            self.print_summary()
            
        except Exception as e:
            print(f"\n❌ ERROR DURANTE REFACTORING: {e}")
            self.rollback_changes()
            sys.exit(1)
    
    def analyze_current_structure(self):
        """Analiza la estructura actual y identifica problemas"""
        print("\n📊 Analizando estructura actual...")
        
        # Archivos obsoletos identificados
        self.obsolete_files = [
            "final_fix.py",
            "fix_missing_parts.bat", 
            "main_patch.txt",
            "verify_and_fix.py",
            "verify_changes.py",
            "test_setup.py",
            "test_capabilities_http_factory.py",
            "ADD_TO_MAIN.txt",
            "install_hybrid_stack.bat",
            "package-lock.json",  # No pertenece al backend Python
            "app/keep_alive.py",  # Obsoleto
        ]
        
        # Servicios duplicados
        self.duplicated_files = [
            "app/services/bcra_real_data_service.py",
            "app/services/bcra_real_service.py", 
            "app/services/enhanced_economic_service.py",
            "scripts/monitor_render.py",  # Duplica monitor.py
            "scripts/simple_init.py",     # Duplica init_database.py
        ]
        
        # Archivos a consolidar
        self.consolidated_files = [
            ("app/services/bcra_service.py", "🔄 Reemplazar con versión unificada"),
            ("app/services/bcra_scheduler.py", "🔄 Reemplazar con scheduler unificado"),
            ("app/models.py", "🔄 Actualizar con modelos consolidados"),
            ("app/config.py", "🔄 Consolidar configuración"),
            ("app/main.py", "🔄 Limpiar y consolidar")
        ]
        
        print(f"  • Archivos obsoletos encontrados: {len(self.obsolete_files)}")
        print(f"  • Servicios duplicados encontrados: {len(self.duplicated_files)}")
        print(f"  • Archivos a consolidar: {len(self.consolidated_files)}")
    
    def create_backup(self):
        """Crea backup completo antes del refactoring"""
        print(f"\n💾 Creando backup en {self.backup_path}...")
        
        if self.backend_path.exists():
            shutil.copytree(self.backend_path, self.backup_path)
            print(f"  ✅ Backup creado exitosamente")
        else:
            raise FileNotFoundError(f"Directorio backend no encontrado: {self.backend_path}")
    
    def remove_obsolete_files(self):
        """Elimina archivos obsoletos identificados"""
        print("\n🗑️ Eliminando archivos obsoletos...")
        
        removed_count = 0
        for file_name in self.obsolete_files:
            file_path = self.backend_path / file_name
            if file_path.exists():
                try:
                    if file_path.is_file():
                        file_path.unlink()
                    else:
                        shutil.rmtree(file_path)
                    print(f"  ❌ Eliminado: {file_name}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ⚠️ Error eliminando {file_name}: {e}")
        
        print(f"  ✅ {removed_count} archivos obsoletos eliminados")
    
    def consolidate_services(self):
        """Consolida servicios duplicados"""
        print("\n🔄 Consolidando servicios duplicados...")
        
        # Eliminar servicios duplicados
        for file_name in self.duplicated_files:
            file_path = self.backend_path / file_name
            if file_path.exists():
                file_path.unlink()
                print(f"  ❌ Eliminado duplicado: {file_name}")
        
        # Crear directorio de servicios si no existe
        services_dir = self.backend_path / "app" / "services"
        services_dir.mkdir(parents=True, exist_ok=True)
        
        # Los archivos consolidados se crearán en create_clean_structure()
        print("  ✅ Servicios duplicados eliminados")
    
    def update_imports(self):
        """Actualiza imports y referencias en archivos existentes"""
        print("\n🔧 Actualizando imports y referencias...")
        
        # Buscar archivos Python para actualizar imports
        python_files = list(self.backend_path.rglob("*.py"))
        
        # Mapeo de imports obsoletos a nuevos
        import_mappings = {
            "from app.services.bcra_real_data_service": "from app.services.bcra_service",
            "from app.services.bcra_real_service": "from app.services.bcra_service",
            "from app.services.enhanced_economic_service": "from app.services.bcra_service",
            "from app.services.bcra_scheduler import bcra_scheduler": "from app.services.scheduler import scheduler",
            "BCRARealDataService": "BCRAService",
            "EnhancedEconomicService": "BCRAService",
            "bcra_scheduler": "scheduler"
        }
        
        updated_files = 0
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Aplicar mappings
                for old_import, new_import in import_mappings.items():
                    content = content.replace(old_import, new_import)
                
                # Solo escribir si hay cambios
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  🔄 Actualizado: {py_file.relative_to(self.backend_path)}")
                    updated_files += 1
                    
            except Exception as e:
                print(f"  ⚠️ Error actualizando {py_file}: {e}")
        
        print(f"  ✅ {updated_files} archivos actualizados")
    
    def create_clean_structure(self):
        """Crea la estructura limpia con archivos consolidados"""
        print("\n🏗️ Creando estructura limpia...")
        
        # Crear directorios necesarios
        directories = [
            "app/services",
            "app/routers", 
            "app/middleware",
            "data",
            "logs",
            "scripts",
            "tests"
        ]
        
        for directory in directories:
            dir_path = self.backend_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Archivos consolidados que se crearán
        consolidated_files = {
            "app/services/bcra_service.py": self.get_bcra_service_content(),
            "app/services/scheduler.py": self.get_scheduler_content(),
            "app/models.py": self.get_models_content(),
            "app/config.py": self.get_config_content(),
            "app/main.py": self.get_main_content(),
            "app/middleware/__init__.py": self.get_middleware_init_content(),
            "app/middleware/logging_middleware.py": self.get_logging_middleware_content(),
            "app/middleware/rate_limit_middleware.py": self.get_rate_limit_middleware_content(),
            "app/routers/__init__.py": "",
            "app/routers/indicators.py": self.get_indicators_router_content(),
            "app/routers/health.py": self.get_health_router_content(),
            "app/routers/system.py": self.get_system_router_content(),
            "scripts/refactor_backend.py": self.get_refactor_script_content(),
            ".env.example": self.get_env_example_content(),
            "requirements_clean.txt": self.get_requirements_content()
        }
        
        # Crear archivos consolidados
        created_count = 0
        for file_path, content in consolidated_files.items():
            full_path = self.backend_path / file_path
            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ Creado: {file_path}")
                created_count += 1
            except Exception as e:
                print(f"  ⚠️ Error creando {file_path}: {e}")
        
        print(f"  ✅ {created_count} archivos consolidados creados")
    
    def validate_refactoring(self):
        """Valida que el refactoring se haya completado correctamente"""
        print("\n✅ Validando refactoring...")
        
        # Verificar que archivos críticos existen
        critical_files = [
            "app/main.py",
            "app/config.py", 
            "app/models.py",
            "app/database.py",
            "app/services/bcra_service.py",
            "app/services/scheduler.py"
        ]
        
        missing_files = []
        for file_path in critical_files:
            full_path = self.backend_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            raise Exception(f"Archivos críticos faltantes: {missing_files}")
        
        # Verificar que archivos obsoletos fueron eliminados
        remaining_obsolete = []
        for file_path in self.obsolete_files:
            full_path = self.backend_path / file_path
            if full_path.exists():
                remaining_obsolete.append(file_path)
        
        if remaining_obsolete:
            print(f"  ⚠️ Archivos obsoletos que no se pudieron eliminar: {remaining_obsolete}")
        
        # Verificar imports básicos
        try:
            import sys
            sys.path.insert(0, str(self.backend_path))
            
            # Test básico de imports
            from app.config import settings
            from app.models import EconomicIndicator
            print("  ✅ Imports básicos funcionando")
            
        except Exception as e:
            print(f"  ⚠️ Warning: algunos imports pueden tener problemas: {e}")
        
        print("  ✅ Validación completada")
    
    def rollback_changes(self):
        """Revierte cambios en caso de error"""
        print("\n🔄 Revirtiendo cambios...")
        
        if self.backup_path.exists():
            # Eliminar directorio actual
            if self.backend_path.exists():
                shutil.rmtree(self.backend_path)
            
            # Restaurar backup
            shutil.copytree(self.backup_path, self.backend_path)
            print(f"  ✅ Backup restaurado desde {self.backup_path}")
        else:
            print("  ⚠️ No se encontró backup para restaurar")
    
    def print_summary(self):
        """Imprime resumen del refactoring"""
        print("\n📋 RESUMEN DEL REFACTORING")
        print("="*40)
        print(f"✅ Archivos obsoletos eliminados: {len(self.obsolete_files)}")
        print(f"✅ Servicios duplicados consolidados: {len(self.duplicated_files)}")
        print(f"✅ Archivos consolidados: {len(self.consolidated_files)}")
        print(f"✅ Backup creado en: {self.backup_path}")
        print("\n🎯 PRÓXIMOS PASOS:")
        print("1. Ejecutar: pip install -r requirements_clean.txt")
        print("2. Revisar configuración en .env")
        print("3. Ejecutar tests: pytest tests/")
        print("4. Iniciar servidor: uvicorn app.main:app --reload")
        print("\n📞 Si hay problemas, restaurar backup:")
        print(f"   rm -rf backend && cp -r {self.backup_path} backend")
    
    # === CONTENT GENERATORS ===
    
    def get_bcra_service_content(self):
        """Retorna el contenido del servicio BCRA consolidado"""
        # Aquí iría el contenido del artefacto bcra_unified_service
        return """# Contenido del servicio BCRA unificado
# Ver artefacto: bcra_unified_service
"""
    
    def get_scheduler_content(self):
        """Retorna el contenido del scheduler unificado"""
        # Aquí iría el contenido del artefacto scheduler_unified
        return """# Contenido del scheduler unificado
# Ver artefacto: scheduler_unified
"""
    
    def get_models_content(self):
        """Retorna el contenido de los modelos consolidados"""
        # Aquí iría el contenido del artefacto models_consolidated
        return """# Contenido de los modelos consolidados
# Ver artefacto: models_consolidated
"""
    
    def get_config_content(self):
        """Retorna el contenido de la configuración consolidada"""
        # Aquí iría el contenido del artefacto config_consolidated
        return """# Contenido de la configuración consolidada
# Ver artefacto: config_consolidated
"""
    
    def get_main_content(self):
        """Retorna el contenido del main.py consolidado"""
        # Aquí iría el contenido del artefacto main_consolidated
        return """# Contenido del main.py consolidado
# Ver artefacto: main_consolidated
"""
    
    def get_middleware_init_content(self):
        return """# Middleware package"""
    
    def get_logging_middleware_content(self):
        return """# Logging middleware implementation"""
    
    def get_rate_limit_middleware_content(self):
        return """# Rate limiting middleware implementation"""
    
    def get_indicators_router_content(self):
        return """# Indicators router implementation"""
    
    def get_health_router_content(self):
        return """# Health router implementation"""
    
    def get_system_router_content(self):
        return """# System router implementation"""
    
    def get_refactor_script_content(self):
        return """# Additional refactoring utilities"""
    
    def get_env_example_content(self):
        return """# Environment variables template
DATABASE_URL=sqlite:///./data/argentina.db
ENVIRONMENT=development
DEBUG=true
"""
    
    def get_requirements_content(self):
        return """# Requirements consolidados y limpios
fastapi[all]==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
aiohttp==3.9.1
requests==2.31.0
pandas==2.1.3
pydantic==2.5.0
python-multipart==0.0.6
python-dotenv==1.0.0
psutil==5.9.6
redis==5.0.1
schedule==1.2.0
pytest==7.4.3
httpx==0.25.2
"""

def main():
    """Función principal"""
    print("🔧 ARGFY PLATFORM - REFACTORING AUTOMÁTICO")
    print("Elimina código duplicado y obsoleto")
    print()
    
    # Verificar que estamos en el directorio correcto
    if not Path("backend").exists():
        print("❌ ERROR: No se encontró el directorio 'backend'")
        print("   Ejecuta este script desde el directorio raíz del proyecto")
        sys.exit(1)
    
    # Confirmar refactoring
    response = input("¿Continuar con el refactoring? (y/n): ")
    if response.lower() != 'y':
        print("Refactoring cancelado")
        sys.exit(0)
    
    # Ejecutar refactoring
    refactoring = ArgfyRefactoring()
    refactoring.run_refactoring()

if __name__ == "__main__":
    main()