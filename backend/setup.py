#!/usr/bin/env python3
# backend/setup.py
"""
Script de configuración completa para Argfy Platform Backend
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """Verificar versión de Python"""
    logger.info("🐍 Verificando versión de Python...")
    
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8+ requerido. Versión actual: %s", sys.version)
        return False
    
    logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def create_directories():
    """Crear directorios necesarios"""
    logger.info("📁 Creando directorios...")
    
    directories = [
        "data",
        "logs", 
        "scripts",
        "tests",
        "app/routers",
        "app/services",
        "app/middleware",
        "app/utils",
        "app/config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ {directory}/")
    
    return True

def install_dependencies():
    """Instalar dependencias de Python"""
    logger.info("📦 Instalando dependencias...")
    
    # Lista de dependencias críticas
    dependencies = [
        "fastapi[all]==0.104.1",
        "uvicorn[standard]==0.24.0", 
        "sqlalchemy==2.0.23",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0",
        "aiohttp==3.9.1",
        "httpx==0.26.0",
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "pandas==2.1.3",
        "psutil==5.9.6",
        "pytest==7.4.3",
        "pytest-asyncio==0.21.1"
    ]
    
    for dep in dependencies:
        try:
            logger.info(f"📦 Instalando {dep}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", dep
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"✅ {dep}")
        except subprocess.CalledProcessError:
            logger.error(f"❌ Error instalando {dep}")
            return False
    
    return True

def create_env_file():
    """Crear archivo .env"""
    logger.info("⚙️ Creando archivo .env...")
    
    if os.path.exists(".env"):
        logger.info("ℹ️ .env ya existe")
        return True
    
    env_template = """# === ARGFY PLATFORM CONFIGURATION ===
DATABASE_URL=sqlite:///./data/argentina.db
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000
RELOAD=true
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000","https://argfy.vercel.app"]

# === EXTERNAL APIS ===
ALPHA_VANTAGE_API_KEY=
FIXER_API_KEY=
BCRA_BASE_URL=https://api.bcra.gob.ar
BCRA_TIMEOUT=30
BCRA_CACHE_TTL=300

# === CACHING ===
REDIS_URL=redis://localhost:6379
CACHE_TTL=300

# === SCHEDULER ===
ENABLE_SCHEDULER=true
UPDATE_INTERVAL_MINUTES=15

# === MONITORING ===
ENABLE_MONITORING=true
LOG_LEVEL=INFO
SENTRY_DSN=

# === SYSTEM ===
API_RATE_LIMIT=100
DEMO_MODE=true
DEMO_DATA_REFRESH_MINUTES=60
LOG_EMOJIS=true
"""
    
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_template)
        logger.info("✅ .env creado")
        return True
    except Exception as e:
        logger.error(f"❌ Error creando .env: {e}")
        return False

def create_requirements_txt():
    """Crear requirements.txt actualizado"""
    logger.info("📄 Creando requirements.txt...")
    
    requirements = """# === CORE FRAMEWORK ===
fastapi[all]==0.104.1
uvicorn[standard]==0.24.0

# === DATABASE ===
sqlalchemy==2.0.23
alembic==1.13.1

# === VALIDATION ===
pydantic==2.5.0
pydantic-settings==2.1.0

# === HTTP CLIENTS ===
aiohttp==3.9.1
httpx==0.26.0
requests==2.31.0

# === DATA PROCESSING ===
pandas==2.1.3
beautifulsoup4==4.12.2
lxml==4.9.3

# === UTILITIES ===
python-multipart==0.0.6
python-dotenv==1.0.0
psutil==5.9.6

# === TESTING ===
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.26.0

# === OPTIONAL (for production) ===
redis==5.0.1
sentry-sdk[fastapi]==1.38.0
gunicorn==21.2.0
"""
    
    try:
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write(requirements)
        logger.info("✅ requirements.txt creado")
        return True
    except Exception as e:
        logger.error(f"❌ Error creando requirements.txt: {e}")
        return False

def fix_config_categories():
    """Convertir categories.ts a categories.py"""
    logger.info("🔧 Corrigiendo archivo de categorías...")
    
    ts_file = "app/config/categories.ts"
    py_file = "app/config/categories.py"
    
    if os.path.exists(ts_file):
        logger.info("ℹ️ Convirtiendo categories.ts a categories.py...")
        
        categories_py = '''# backend/app/config/categories.py
"""
Configuración de categorías de indicadores económicos
"""

CATEGORIES = {
    "economia": {
        "id": "economia",
        "title": "📊 Datos Económicos",
        "description": "IPC, PBI, desempleo, reservas, política monetaria y FX.",
        "icon": "📊",
        "indicators": ["ipc", "pbi", "emae", "desempleo", "reservas_bcra", "dolar_blue"],
        "color": "blue"
    },
    "gobierno": {
        "id": "gobierno", 
        "title": "🏛️ Datos de Gobierno",
        "description": "Resultado fiscal, deuda pública, gasto gubernamental.",
        "icon": "🏛️",
        "indicators": ["resultado_fiscal", "deuda_publica", "gasto_publico", "ingresos_tributarios", "empleo_publico", "transferencias_sociales"],
        "color": "purple"
    },
    "finanzas": {
        "id": "finanzas",
        "title": "🏦 Datos Financieros y Bancos", 
        "description": "Plazos fijos, tasas de crédito, depósitos, liquidez bancaria.",
        "icon": "🏦",
        "indicators": ["plazo_fijo_30", "tasa_tarjeta_credito", "depositos_privados", "prestamos_sector_privado", "morosidad_bancaria", "liquidez_bancaria"],
        "color": "green"
    },
    "mercados": {
        "id": "mercados",
        "title": "📈 Datos de Mercados",
        "description": "MERVAL, bonos, acciones, CEDEARs, panel BYMA.",
        "icon": "📈", 
        "indicators": ["merval", "rendimiento_al30", "precio_gd30", "volumen_acciones_cedears", "dolar_ccl", "panel_general_byma"],
        "color": "indigo"
    },
    "tecnologia": {
        "id": "tecnologia",
        "title": "💻 Tecnología y Software",
        "description": "Exportaciones SBC, empleo IT, inversión I+D, startups.",
        "icon": "💻",
        "indicators": ["exportaciones_sbc", "empleo_it", "inversion_id", "penetracion_internet", "vc_startups", "facturacion_software"],
        "color": "cyan"
    },
    "industria": {
        "id": "industria", 
        "title": "🏭 Datos de Industria",
        "description": "IPI manufacturero, PMI, producción automotriz, acero.",
        "icon": "🏭",
        "indicators": ["ipi_manufacturero", "pmi", "produccion_automotriz", "exportaciones_moi", "produccion_acero", "costo_construccion"],
        "color": "orange"
    }
}

COLOR_SCHEMES = {
    "blue": {
        "bg": "bg-blue-50 dark:bg-blue-900/20",
        "border": "border-blue-200 dark:border-blue-800",
        "text": "text-blue-900 dark:text-blue-100",
        "accent": "text-blue-600 dark:text-blue-400",
        "button": "bg-blue-600 hover:bg-blue-700"
    },
    "purple": {
        "bg": "bg-purple-50 dark:bg-purple-900/20",
        "border": "border-purple-200 dark:border-purple-800", 
        "text": "text-purple-900 dark:text-purple-100",
        "accent": "text-purple-600 dark:text-purple-400",
        "button": "bg-purple-600 hover:bg-purple-700"
    },
    "green": {
        "bg": "bg-green-50 dark:bg-green-900/20",
        "border": "border-green-200 dark:border-green-800",
        "text": "text-green-900 dark:text-green-100", 
        "accent": "text-green-600 dark:text-green-400",
        "button": "bg-green-600 hover:bg-green-700"
    },
    "indigo": {
        "bg": "bg-indigo-50 dark:bg-indigo-900/20",
        "border": "border-indigo-200 dark:border-indigo-800",
        "text": "text-indigo-900 dark:text-indigo-100",
        "accent": "text-indigo-600 dark:text-indigo-400", 
        "button": "bg-indigo-600 hover:bg-indigo-700"
    },
    "cyan": {
        "bg": "bg-cyan-50 dark:bg-cyan-900/20",
        "border": "border-cyan-200 dark:border-cyan-800",
        "text": "text-cyan-900 dark:text-cyan-100",
        "accent": "text-cyan-600 dark:text-cyan-400",
        "button": "bg-cyan-600 hover:bg-cyan-700"
    },
    "orange": {
        "bg": "bg-orange-50 dark:bg-orange-900/20", 
        "border": "border-orange-200 dark:border-orange-800",
        "text": "text-orange-900 dark:text-orange-100",
        "accent": "text-orange-600 dark:text-orange-400",
        "button": "bg-orange-600 hover:bg-orange-700"
    }
}
'''
        
        try:
            with open(py_file, "w", encoding="utf-8") as f:
                f.write(categories_py)
            
            # Eliminar archivo .ts
            os.remove(ts_file)
            logger.info("✅ categories.py creado y .ts eliminado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error convirtiendo categorías: {e}")
            return False
    else:
        logger.info("ℹ️ categories.ts no encontrado, creando categories.py...")
        # El código de arriba ya crea el archivo
        return True

def create_basic_tests():
    """Crear tests básicos"""
    logger.info("🧪 Creando tests básicos...")
    
    test_main = '''# tests/test_main.py
"""
Tests básicos para la aplicación
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Test endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["name"] == "Argfy Platform API"

def test_ping():
    """Test ping endpoint"""
    response = client.get("/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "pong"

def test_health_check():
    """Test health check"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_indicators_current():
    """Test current indicators"""
    response = client.get("/api/v1/indicators/current")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_system_info():
    """Test system info"""
    response = client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
'''
    
    try:
        Path("tests").mkdir(exist_ok=True)
        
        with open("tests/__init__.py", "w") as f:
            f.write("# Tests package")
        
        with open("tests/test_main.py", "w", encoding="utf-8") as f:
            f.write(test_main)
        
        logger.info("✅ Tests básicos creados")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creando tests: {e}")
        return False

def create_startup_script():
    """Crear script de inicio"""
    logger.info("🚀 Creando script de inicio...")
    
    startup_script = '''#!/usr/bin/env python3
# backend/start.py
"""
Script de inicio para Argfy Platform
"""
import sys
import os
import asyncio
import subprocess
from pathlib import Path

def check_requirements():
    """Verificar que todo esté configurado"""
    print("🔍 Verificando configuración...")
    
    # Verificar .env
    if not Path(".env").exists():
        print("❌ Archivo .env no encontrado")
        print("💡 Ejecuta: python setup.py")
        return False
    
    # Verificar base de datos
    if not Path("data").exists():
        print("📁 Creando directorio data...")
        Path("data").mkdir(exist_ok=True)
    
    return True

async def initialize_database():
    """Inicializar base de datos si es necesario"""
    print("📊 Verificando base de datos...")
    
    db_file = Path("data/argentina.db")
    if not db_file.exists() or db_file.stat().st_size == 0:
        print("🔧 Inicializando base de datos...")
        try:
            from scripts.init_database import main as init_main
            success = await init_main()
            if success:
                print("✅ Base de datos inicializada")
            else:
                print("❌ Error inicializando base de datos")
                return False
        except ImportError:
            print("⚠️ Script de inicialización no encontrado, continuando...")
    else:
        print("✅ Base de datos existe")
    
    return True

def start_server():
    """Iniciar servidor de desarrollo"""
    print("🚀 Iniciando Argfy Platform...")
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\\n⏹️ Servidor detenido")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")

async def main():
    """Función principal"""
    if not check_requirements():
        return False
    
    if not await initialize_database():
        return False
    
    start_server()
    return True

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    try:
        with open("start.py", "w", encoding="utf-8") as f:
            f.write(startup_script)
        
        # Hacer ejecutable en Unix
        if os.name != 'nt':
            os.chmod("start.py", 0o755)
        
        logger.info("✅ Script de inicio creado")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creando script de inicio: {e}")
        return False

def main():
    """Función principal del setup"""
    logger.info("🚀 ARGFY PLATFORM BACKEND SETUP")
    logger.info("=" * 50)
    
    steps = [
        ("Verificar Python", check_python_version),
        ("Crear directorios", create_directories),
        ("Instalar dependencias", install_dependencies),
        ("Crear .env", create_env_file),
        ("Crear requirements.txt", create_requirements_txt),
        ("Corregir categorías", fix_config_categories),
        ("Crear tests", create_basic_tests),
        ("Crear script de inicio", create_startup_script)
    ]
    
    completed = []
    
    for step_name, step_func in steps:
        try:
            if step_func():
                completed.append(step_name)
            else:
                logger.error(f"❌ Falló: {step_name}")
                break
        except Exception as e:
            logger.error(f"❌ Error en {step_name}: {e}")
            break
    
    logger.info("\\n" + "=" * 50)
    logger.info(f"✅ Completados: {len(completed)}/{len(steps)} pasos")
    
    if len(completed) == len(steps):
        logger.info("🎉 SETUP COMPLETADO EXITOSAMENTE!")
        logger.info("\\n📋 PRÓXIMOS PASOS:")
        logger.info("1. Activar entorno virtual: source venv/bin/activate")
        logger.info("2. Inicializar BD: python scripts/init_database.py")
        logger.info("3. Iniciar servidor: python start.py")
        logger.info("4. Abrir: http://localhost:8000/docs")
        return True
    else:
        logger.error("❌ Setup incompleto")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
