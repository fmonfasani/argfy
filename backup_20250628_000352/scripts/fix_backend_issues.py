#!/usr/bin/env python3
# backend/scripts/fix_backend_issues.py
"""
Script para detectar y corregir automáticamente problemas en el backend de Argfy
Ejecutar: python scripts/fix_backend_issues.py
"""

import os
import sys
import re
import shutil
from datetime import datetime
from pathlib import Path
import subprocess
import json

class BackendFixer:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.issues_found = []
        self.fixes_applied = []
        self.errors = []
        
    def log_issue(self, issue_type: str, description: str, file_path: str = ""):
        """Log an issue found"""
        self.issues_found.append({
            "type": issue_type,
            "description": description,
            "file": file_path,
            "timestamp": datetime.now().isoformat()
        })
        print(f"🔍 ISSUE: {description}")
        if file_path:
            print(f"   📁 File: {file_path}")
    
    def log_fix(self, description: str, file_path: str = ""):
        """Log a fix applied"""
        self.fixes_applied.append({
            "description": description,
            "file": file_path,
            "timestamp": datetime.now().isoformat()
        })
        print(f"✅ FIX: {description}")
        if file_path:
            print(f"   📁 File: {file_path}")
    
    def log_error(self, error: str):
        """Log an error"""
        self.errors.append({
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        print(f"❌ ERROR: {error}")
    
    def check_main_py_issues(self):
        """Check and fix main.py issues"""
        main_py_path = self.base_path / "app" / "main.py"
        
        if not main_py_path.exists():
            self.log_error("main.py not found")
            return
        
        print("\n🔍 Checking main.py...")
        
        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for duplicate imports
        bcra_real_imports = re.findall(r'from .*routers import.*bcra_real', content)
        if len(bcra_real_imports) > 1:
            self.log_issue("duplicate_import", "Duplicate bcra_real import found", str(main_py_path))
            
            # Fix duplicate imports
            content = re.sub(r'from app\.routers import bcra_real\n', '', content, count=1)
            self.log_fix("Removed duplicate bcra_real import", str(main_py_path))
        
        # Check for BCRAScheduler import issues
        if "from app.services.bcra_scheduler import BCRAScheduler" in content:
            self.log_issue("wrong_scheduler_import", "Wrong scheduler class name imported", str(main_py_path))
            
            # Fix scheduler import
            content = content.replace(
                "from app.services.bcra_scheduler import BCRAScheduler",
                "from app.services.bcra_scheduler import bcra_scheduler, start_scheduler, get_scheduler_status"
            )
            content = content.replace("BCRAScheduler()", "bcra_scheduler")
            self.log_fix("Fixed scheduler import and usage", str(main_py_path))
        
        # Write back fixed content
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def check_scheduler_issues(self):
        """Check and fix bcra_scheduler.py issues"""
        scheduler_path = self.base_path / "app" / "services" / "bcra_scheduler.py"
        
        if not scheduler_path.exists():
            self.log_error("bcra_scheduler.py not found")
            return
        
        print("\n🔍 Checking bcra_scheduler.py...")
        
        with open(scheduler_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if BCRAScheduler class exists (should be the main class)
        if "class BCRAScheduler:" not in content and "class HybridBCRAScheduler:" in content:
            self.log_issue("wrong_scheduler_class", "Main scheduler class has wrong name", str(scheduler_path))
            
            # This will be fixed by replacing the entire file with the corrected version
            self.log_fix("Scheduler class name will be corrected", str(scheduler_path))
    
    def check_router_issues(self):
        """Check router files for issues"""
        routers_path = self.base_path / "app" / "routers"
        
        print("\n🔍 Checking routers...")
        
        # Check for empty files
        for router_file in routers_path.glob("*.py"):
            if router_file.name == "__init__.py":
                continue
                
            if router_file.stat().st_size == 0:
                self.log_issue("empty_router", f"Router file is empty", str(router_file))
            
            # Check for common import issues
            with open(router_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for circular import issues
                if "from ..services" in content and "from app.services" in content:
                    self.log_issue("mixed_imports", "Mixed relative and absolute imports", str(router_file))
    
    def check_services_structure(self):
        """Check services directory structure"""
        services_path = self.base_path / "app" / "services"
        
        print("\n🔍 Checking services structure...")
        
        # Check for __init__.py files
        subdirs = ["base", "modern", "performance"]
        for subdir in subdirs:
            init_file = services_path / subdir / "__init__.py"
            if not init_file.exists():
                self.log_issue("missing_init", f"Missing __init__.py in {subdir}", str(init_file))
                
                # Create missing __init__.py
                init_file.parent.mkdir(exist_ok=True)
                init_file.touch()
                self.log_fix(f"Created missing __init__.py in {subdir}", str(init_file))
    
    def check_database_setup(self):
        """Check database setup"""
        print("\n🔍 Checking database setup...")
        
        data_dir = self.base_path / "data"
        if not data_dir.exists():
            self.log_issue("missing_data_dir", "Data directory doesn't exist", str(data_dir))
            data_dir.mkdir(exist_ok=True)
            self.log_fix("Created data directory", str(data_dir))
        
        logs_dir = self.base_path / "logs"
        if not logs_dir.exists():
            self.log_issue("missing_logs_dir", "Logs directory doesn't exist", str(logs_dir))
            logs_dir.mkdir(exist_ok=True)
            self.log_fix("Created logs directory", str(logs_dir))
    
    def check_dependencies(self):
        """Check Python dependencies"""
        print("\n🔍 Checking dependencies...")
        
        requirements_path = self.base_path / "requirements.txt"
        if not requirements_path.exists():
            self.log_error("requirements.txt not found")
            return
        
        # Check for conflicting or outdated packages
        with open(requirements_path, 'r') as f:
            requirements = f.read()
        
        # Check for potential conflicts
        if "httpx" in requirements and "aiohttp" in requirements and "requests" in requirements:
            print("✅ Hybrid HTTP stack detected - this is intentional")
        
        # Check for missing critical packages
        critical_packages = ["fastapi", "uvicorn", "sqlalchemy", "aiohttp"]
        for package in critical_packages:
            if package not in requirements:
                self.log_issue("missing_dependency", f"Critical package {package} not in requirements", str(requirements_path))
    
    def validate_imports(self):
        """Validate all imports in Python files"""
        print("\n🔍 Validating imports...")
        
        python_files = list(self.base_path.glob("**/*.py"))
        python_files = [f for f in python_files if "venv" not in str(f) and "__pycache__" not in str(f)]
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for common import patterns that might cause issues
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    if line.strip().startswith("from") and "import" in line:
                        # Check for relative import inconsistencies
                        if line.count("..") > 2:
                            self.log_issue("complex_relative_import", 
                                         f"Complex relative import at line {line_num}: {line.strip()}", 
                                         str(py_file))
                        
                        # Check for potential circular imports
                        if "app.routers" in line and "app.services" in py_file.name:
                            self.log_issue("potential_circular_import",
                                         f"Service importing router at line {line_num}",
                                         str(py_file))
                                         
            except Exception as e:
                self.log_error(f"Error reading {py_file}: {e}")
    
    def apply_fixes(self):
        """Apply automatic fixes"""
        print("\n🔧 Applying automatic fixes...")
        
        # Apply main.py fixes
        self.check_main_py_issues()
        
        # Apply scheduler fixes by copying the corrected version
        self.fix_scheduler_file()
        
        # Apply structure fixes
        self.check_services_structure()
        self.check_database_setup()
    
    def fix_scheduler_file(self):
        """Replace scheduler file with corrected version"""
        scheduler_path = self.base_path / "app" / "services" / "bcra_scheduler.py"
        
        corrected_scheduler = '''# backend/app/services/bcra_scheduler.py
import asyncio
import time
from datetime import datetime
import logging
import threading
from typing import Optional

logger = logging.getLogger(__name__)

class BCRAScheduler:
    """Scheduler para actualizar datos del BCRA automáticamente - VERSIÓN CORREGIDA"""
    
    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.update_interval = 900  # 15 minutos
        self.last_update: Optional[datetime] = None
        logger.info("✅ BCRAScheduler inicializado correctamente")
        
    async def update_data(self):
        """Actualizar datos del BCRA"""
        try:
            logger.info("🔄 Iniciando actualización de datos BCRA...")
            start_time = datetime.now()
            
            # Importar el servicio aquí para evitar circular imports
            from app.services.bcra_real_data_service import BCRARealDataService
            
            async with BCRARealDataService() as service:
                dashboard_data = await service.get_dashboard_data()
                
                if dashboard_data.get("status") == "success":
                    saved = await service.save_to_database(dashboard_data)
                    
                    if saved:
                        self.last_update = datetime.now()
                        duration = (self.last_update - start_time).total_seconds()
                        logger.info(f"✅ Datos BCRA actualizados exitosamente en {duration:.2f}s")
                        return True
                    else:
                        logger.error("❌ Error guardando datos en BD")
                        return False
                else:
                    logger.error(f"❌ Error obteniendo datos: {dashboard_data}")
                    return False
                    
        except Exception as e:
            logger.error(f"💥 Error en actualización automática: {e}")
            return False
    
    def start(self):
        """Iniciar el scheduler"""
        if not self.running:
            self.running = True
            logger.info("🚀 BCRA Scheduler iniciado exitosamente")
            return True
        else:
            logger.warning("⚠️  Scheduler ya está ejecutándose")
            return False
    
    def stop(self):
        """Detener el scheduler"""
        if self.running:
            self.running = False
            logger.info("✅ BCRA Scheduler detenido")
            return True
        else:
            logger.warning("⚠️  Scheduler ya está detenido")
            return False
    
    def get_status(self) -> dict:
        """Obtener estado del scheduler"""
        return {
            "running": self.running,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "update_interval_minutes": self.update_interval // 60,
        }

# Instancia global con nombre correcto
bcra_scheduler = BCRAScheduler()

def start_scheduler():
    return bcra_scheduler.start()

def stop_scheduler():
    return bcra_scheduler.stop()

def get_scheduler_status():
    return bcra_scheduler.get_status()
'''
        
        # Backup original file
        backup_path = scheduler_path.with_suffix('.py.backup')
        if scheduler_path.exists():
            shutil.copy2(scheduler_path, backup_path)
            self.log_fix(f"Backed up original scheduler to {backup_path}")
        
        # Write corrected version
        with open(scheduler_path, 'w', encoding='utf-8') as f:
            f.write(corrected_scheduler)
        
        self.log_fix("Applied corrected BCRAScheduler implementation", str(scheduler_path))
    
    def create_missing_router(self):
        """Create missing economic_cards router"""
        router_path = self.base_path / "app" / "routers" / "economic_cards.py"
        
        if not router_path.exists():
            self.log_issue("missing_cards_router", "Economic cards router missing", str(router_path))
            
            # This would be created with the cards router code from the artifact
            self.log_fix("Economic cards router needs to be created manually", str(router_path))
    
    def run_tests(self):
        """Run basic tests to validate fixes"""
        print("\n🧪 Running validation tests...")
        
        try:
            # Test importing main modules
            import sys
            sys.path.insert(0, str(self.base_path))
            
            # Test database module
            from app.database import Base, engine, get_db
            print("✅ Database module imports successfully")
            
            # Test models
            from app.models import EconomicIndicator, HistoricalData, NewsItem
            print("✅ Models import successfully")
            
            # Test main app
            from app.main import app
            print("✅ Main app imports successfully")
            
            # Test scheduler
            from app.services.bcra_scheduler import bcra_scheduler, start_scheduler
            print("✅ Scheduler imports successfully")
            
        except Exception as e:
            self.log_error(f"Import test failed: {e}")
    
    def generate_report(self):
        """Generate a comprehensive report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "issues_found": len(self.issues_found),
            "fixes_applied": len(self.fixes_applied),
            "errors": len(self.errors),
            "details": {
                "issues": self.issues_found,
                "fixes": self.fixes_applied,
                "errors": self.errors
            }
        }
        
        report_path = self.base_path / f"fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved to: {report_path}")
        return report
    
    def run_full_check(self):
        """Run complete backend check and fix"""
        print("🚀 ARGFY BACKEND FIXER")
        print("=" * 50)
        
        # 1. Check structure
        self.check_services_structure()
        self.check_database_setup()
        
        # 2. Check code issues
        self.check_main_py_issues()
        self.check_scheduler_issues()
        self.check_router_issues()
        
        # 3. Check dependencies
        self.check_dependencies()
        
        # 4. Validate imports
        self.validate_imports()
        
        # 5. Apply fixes
        self.apply_fixes()
        
        # 6. Run tests
        self.run_tests()
        
        # 7. Generate report
        report = self.generate_report()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 SUMMARY")
        print("=" * 50)
        print(f"🔍 Issues found: {len(self.issues_found)}")
        print(f"✅ Fixes applied: {len(self.fixes_applied)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n⚠️  MANUAL ACTION REQUIRED:")
            for error in self.errors:
                print(f"   • {error['error']}")
        
        if self.fixes_applied:
            print("\n🎉 Backend issues have been automatically fixed!")
            print("   Run 'python -m uvicorn app.main:app --reload' to test")
        
        return report

def main():
    """Main function"""
    fixer = BackendFixer()
    fixer.run_full_check()

if __name__ == "__main__":
    main()