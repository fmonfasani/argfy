import os
import json
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DeploymentPreparation:
    """Preparar la aplicación para deployment"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
    def prepare_for_deployment(self):
        """Preparar todo para deployment"""
        
        print("🚀 PREPARANDO ARGFY PLATFORM PARA DEPLOYMENT")
        print("=" * 50)
        
        checks = [
            ("Backend Configuration", self.check_backend_config),
            ("Frontend Configuration", self.check_frontend_config),
            ("Environment Variables", self.check_environment_variables),
            ("Dependencies", self.check_dependencies),
            ("Security Settings", self.check_security),
            ("Performance Settings", self.check_performance),
            ("Deployment Files", self.create_deployment_files)
        ]
        
        results = {}
        
        for check_name, check_function in checks:
            print(f"\n🔍 {check_name}:")
            try:
                result = check_function()
                results[check_name] = result
                if result.get("status") == "ok":
                    print(f"✅ {result.get('message', 'OK')}")
                else:
                    print(f"⚠️ {result.get('message', 'Warning')}")
            except Exception as e:
                print(f"❌ Error: {e}")
                results[check_name] = {"status": "error", "message": str(e)}
        
        # Generar reporte final
        self.generate_deployment_report(results)
        
        return results
    
    def check_backend_config(self):
        """Verificar configuración del backend"""
        
        # Verificar archivos esenciales
        essential_files = [
            "requirements.txt",
            "app/main.py",
            "app/config/settings.py",
            ".env"
        ]
        
        missing_files = []
        for file_path in essential_files:
            if not (self.backend_dir / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            return {
                "status": "warning",
                "message": f"Missing files: {missing_files}"
            }
        
        # Verificar configuración de producción
        env_file = self.backend_dir / ".env"
        if env_file.exists():
            with open(env_file) as f:
                env_content = f.read()
                if "dev-secret-key" in env_content:
                    return {
                        "status": "warning", 
                        "message": "Development secret key found in .env"
                    }
        
        return {"status": "ok", "message": "Backend configuration ready"}
    
    def check_frontend_config(self):
        """Verificar configuración del frontend"""
        
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            return {"status": "error", "message": "package.json not found"}
        
        with open(package_json) as f:
            package_data = json.load(f)
        
        # Verificar scripts necesarios
        required_scripts = ["build", "start", "dev"]
        missing_scripts = [s for s in required_scripts if s not in package_data.get("scripts", {})]
        
        if missing_scripts:
            return {
                "status": "warning",
                "message": f"Missing scripts: {missing_scripts}"
            }
        
        # Verificar dependencias críticas
        deps = package_data.get("dependencies", {})
        critical_deps = ["next", "react", "recharts"]
        missing_deps = [d for d in critical_deps if d not in deps]
        
        if missing_deps:
            return {
                "status": "warning",
                "message": f"Missing dependencies: {missing_deps}"
            }
        
        return {"status": "ok", "message": "Frontend configuration ready"}
    
    def check_environment_variables(self):
        """Verificar variables de entorno"""
        
        # Variables requeridas para producción
        prod_vars = {
            "DATABASE_URL": "Database connection",
            "SECRET_KEY": "Application secret",
            "CORS_ORIGINS": "Allowed origins",
            "ENVIRONMENT": "Environment setting"
        }
        
        env_file = self.backend_dir / ".env"
        if not env_file.exists():
            return {"status": "error", "message": ".env file not found"}
        
        with open(env_file) as f:
            env_content = f.read()
        
        missing_vars = []
        for var, description in prod_vars.items():
            if var not in env_content:
                missing_vars.append(f"{var} ({description})")
        
        if missing_vars:
            return {
                "status": "warning",
                "message": f"Missing environment variables: {missing_vars}"
            }
        
        return {"status": "ok", "message": "Environment variables configured"}
    
    def check_dependencies(self):
        """Verificar dependencias"""
        
        # Backend dependencies
        requirements_file = self.backend_dir / "requirements.txt"
        if not requirements_file.exists():
            return {"status": "error", "message": "requirements.txt not found"}
        
        # Frontend dependencies
        try:
            result = subprocess.run(
                ["npm", "list", "--depth=0"],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    "status": "warning",
                    "message": "Frontend dependencies may have issues"
                }
        except Exception:
            return {
                "status": "warning", 
                "message": "Could not verify frontend dependencies"
            }
        
        return {"status": "ok", "message": "Dependencies verified"}
    
    def check_security(self):
        """Verificar configuraciones de seguridad"""
        
        issues = []
        
        # Verificar CORS configuration
        main_py = self.backend_dir / "app/main.py"
        if main_py.exists():
            with open(main_py) as f:
                content = f.read()
                if "allow_origins=[\"*\"]" in content:
                    issues.append("CORS allows all origins (security risk)")
        
        # Verificar debug mode
        env_file = self.backend_dir / ".env"
        if env_file.exists():
            with open(env_file) as f:
                content = f.read()
                if "DEBUG=true" in content:
                    issues.append("Debug mode enabled (should be false in production)")
        
        if issues:
            return {
                "status": "warning",
                "message": f"Security issues: {issues}"
            }
        
        return {"status": "ok", "message": "Security configuration looks good"}
    
    def check_performance(self):
        """Verificar configuraciones de performance"""
        
        recommendations = []
        
        # Verificar si hay configuración de cache
        env_file = self.backend_dir / ".env"
        if env_file.exists():
            with open(env_file) as f:
                content = f.read()
                if "REDIS_URL" not in content:
                    recommendations.append("Consider adding Redis for caching")
        
        # Verificar configuración de Next.js
        next_config = self.frontend_dir / "next.config.js"
        if next_config.exists():
            with open(next_config) as f:
                content = f.read()
                if "compress" not in content:
                    recommendations.append("Consider enabling compression in Next.js")
        
        if recommendations:
            return {
                "status": "ok",
                "message": f"Performance recommendations: {recommendations}"
            }
        
        return {"status": "ok", "message": "Performance configuration adequate"}
    
    def create_deployment_files(self):
        """Crear archivos necesarios para deployment"""
        
        # Crear Dockerfile para backend
        backend_dockerfile = self.backend_dir / "Dockerfile"
        if not backend_dockerfile.exists():
            dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
            with open(backend_dockerfile, "w") as f:
                f.write(dockerfile_content)
        
        # Crear render.yaml
        render_yaml = self.project_root / "render.yaml"
        if not render_yaml.exists():
            render_content = '''services:
  - type: web
    name: argfy-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DEBUG
        value: false
'''
            with open(render_yaml, "w") as f:
                f.write(render_content)
        
        # Crear vercel.json para frontend
        vercel_json = self.frontend_dir / "vercel.json"
        if not vercel_json.exists():
            vercel_content = {
                "env": {
                    "NEXT_PUBLIC_BACKEND_URL": "https://argfy-backend.onrender.com",
                    "NEXT_PUBLIC_API_BASE": "https://argfy-backend.onrender.com/api/v1"
                },
                "build": {
                    "env": {
                        "NEXT_TELEMETRY_DISABLED": "1"
                    }
                }
            }
            with open(vercel_json, "w") as f:
                json.dump(vercel_content, f, indent=2)
        
        return {"status": "ok", "message": "Deployment files created"}
    
    def generate_deployment_report(self, results: dict):
        """Generar reporte de deployment"""
        
        print("\n" + "="*60)
        print("📋 DEPLOYMENT READINESS REPORT")
        print("="*60)
        
        all_ok = True
        warnings = 0
        
        for check_name, result in results.items():
            status = result.get("status", "unknown")
            if status == "ok":
                print(f"✅ {check_name}")
            elif status == "warning":
                print(f"⚠️ {check_name}: {result.get('message', '')}")
                warnings += 1
            else:
                print(f"❌ {check_name}: {result.get('message', '')}")
                all_ok = False
        
        print("\n" + "="*60)
        
        if all_ok and warnings == 0:
            print("🎉 READY FOR DEPLOYMENT!")
            print("All checks passed. Platform is ready for production.")
        elif all_ok and warnings > 0:
            print(f"⚠️ MOSTLY READY ({warnings} warnings)")
            print("Platform can be deployed but consider addressing warnings.")
        else:
            print("❌ NOT READY FOR DEPLOYMENT")
            print("Please address the errors before deploying.")
        
        # Guardar reporte
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"deployment_report_{timestamp}.json", "w") as f:
            json.dump({
                "timestamp": timestamp,
                "results": results,
                "ready": all_ok,
                "warnings": warnings
            }, f, indent=2)
        
        print(f"\n📄 Report saved to: deployment_report_{timestamp}.json")


if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            tester = ArgfyTestSuite()
            asyncio.run(tester.run_all_tests())
        elif sys.argv[1] == "performance":
            optimizer = PerformanceOptimizer()
            asyncio.run(optimizer.analyze_performance())
        elif sys.argv[1] == "deploy":
            preparer = DeploymentPreparation()
            preparer.prepare_for_deployment()
    else:
        print("Usage: python script.py [test|performance|deploy]")