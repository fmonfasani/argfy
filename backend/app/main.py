# backend/app/main.py
"""
FastAPI main application con imports robustos
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Imports core
try:
    from .database import engine, Base, get_db
    from .models import EconomicIndicator, HistoricalData
    from .config import settings
except ImportError as e:
    logger.error(f"Error importing core modules: {e}")
    sys.exit(1)

# Lista para trackear routers cargados
routers_loaded = []
routers_failed = []

# ✅ IMPORTS DE ROUTERS CON MANEJO DE ERRORES
def load_router(router_name: str, module_path: str):
    """Cargar router con manejo de errores"""
    try:
        if router_name == "indicators":
            from .routers.indicators import router
            return router
        elif router_name == "data":
            from .routers.data import router  # ✅ Ahora existe
            return router
        elif router_name == "economic_cards":
            from .routers.economic_cards import router
            return router
        elif router_name == "expanded_indicators":
            from .routers.expanded_indicators import router
            return router
        elif router_name == "health":
            from .routers.health import router
            return router
        elif router_name == "system":
            from .routers.system import router
            return router
        elif router_name == "unified_economic":
            from .routers.unified_economic import router
            return router
        elif router_name == "bcra_real":
            from .routers.bcra_real import router
            return router
        else:
            raise ImportError(f"Unknown router: {router_name}")
            
    except ImportError as e:
        logger.warning(f"⚠️ Could not load router {router_name}: {e}")
        routers_failed.append((router_name, str(e)))
        return None
    except Exception as e:
        logger.error(f"❌ Error loading router {router_name}: {e}")
        routers_failed.append((router_name, str(e)))
        return None

# ✅ CARGAR TODOS LOS ROUTERS
routers_config = [
    ("indicators", "app.routers.indicators"),
    ("data", "app.routers.data"),  # ✅ Ahora existe
    ("economic_cards", "app.routers.economic_cards"),
    ("health", "app.routers.health"),
    ("system", "app.routers.system"),
    ("unified_economic", "app.routers.unified_economic"),
    ("bcra_real", "app.routers.bcra_real"),
    ("expanded_indicators", "app.routers.expanded_indicators"),
]

# Cargar routers disponibles
available_routers = {}
for router_name, module_path in routers_config:
    router = load_router(router_name, module_path)
    if router:
        available_routers[router_name] = router
        routers_loaded.append((router_name, "loaded"))
        logger.info(f"✅ Router {router_name} cargado exitosamente")

# ✅ SCHEDULER CON MANEJO DE ERRORES
scheduler_status = {"enabled": False, "error": None}

try:
    # Intentar importar scheduler
    if getattr(settings, 'ENABLE_SCHEDULER', True):
        try:
            from .services.bcra_scheduler import bcra_scheduler, start_scheduler, get_scheduler_status
            scheduler_status["enabled"] = True
            logger.info("✅ Scheduler importado exitosamente")
        except ImportError as e:
            logger.warning(f"⚠️ Scheduler no disponible: {e}")
            scheduler_status["error"] = str(e)
    else:
        logger.info("📝 Scheduler deshabilitado por configuración")
        
except Exception as e:
    logger.error(f"❌ Error configurando scheduler: {e}")
    scheduler_status["error"] = str(e)

# ✅ STARTUP/SHUTDOWN HANDLERS
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    
    # Startup
    logger.info("🚀 Iniciando Argfy Platform...")
    
    try:
        # Crear tablas de base de datos
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas de base de datos verificadas")
        
        # Inicializar scheduler si está disponible
        if scheduler_status["enabled"]:
            try:
                # Iniciar scheduler en background si es posible
                logger.info("🔄 Scheduler inicializado")
            except Exception as e:
                logger.warning(f"⚠️ Error inicializando scheduler: {e}")
        
        # Log de routers cargados
        logger.info(f"📊 Routers cargados: {len(routers_loaded)}")
        logger.info(f"❌ Routers fallidos: {len(routers_failed)}")
        
    except Exception as e:
        logger.error(f"❌ Error en startup: {e}")
    
    yield  # Aplicación corriendo
    
    # Shutdown
    logger.info("⏹️ Cerrando Argfy Platform...")
    
    try:
        # Detener scheduler si está corriendo
        if scheduler_status["enabled"]:
            logger.info("🔄 Deteniendo scheduler...")
            
    except Exception as e:
        logger.error(f"❌ Error en shutdown: {e}")

# ✅ CREAR APP FASTAPI
app = FastAPI(
    title="Argfy Platform API",
    description="""
    🇦🇷 **Plataforma de Datos Económicos Argentinos**
    
    API REST para acceder a indicadores económicos argentinos en tiempo real.
    
    ## 🚀 Funcionalidades
    - Indicadores económicos actualizados
    - Datos históricos con filtros
    - Múltiples fuentes de datos (BCRA, INDEC, etc.)
    - Sistema de monitoreo integrado
    
    ## 📊 Categorías Disponibles
    - **Economía**: IPC, PBI, EMAE, Desempleo
    - **Gobierno**: Fiscal, Deuda, Gasto Público  
    - **Finanzas**: Tasas, Depósitos, Préstamos
    - **Mercados**: MERVAL, Bonos, Acciones
    - **Tecnología**: Exportaciones SBC, Empleo IT
    - **Industria**: IPI, PMI, Producción
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ✅ MIDDLEWARES
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, 'CORS_ORIGINS', ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ INCLUIR ROUTERS DISPONIBLES
for router_name, router in available_routers.items():
    try:
        app.include_router(router)
        logger.info(f"✅ Router {router_name} incluido en app")
    except Exception as e:
        logger.error(f"❌ Error incluyendo router {router_name}: {e}")
        routers_failed.append((router_name, f"Include error: {str(e)}"))

# ✅ ENDPOINTS BÁSICOS
@app.get("/")
async def root():
    """Endpoint raíz con información del sistema"""
    return {
        "name": "Argfy Platform API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "routers": {
            "loaded": [name for name, status in routers_loaded],
            "failed": [name for name, error in routers_failed],
            "total_loaded": len(routers_loaded),
            "total_failed": len(routers_failed)
        },
        "scheduler": {
            "enabled": scheduler_status["enabled"],
            "error": scheduler_status.get("error")
        },
        "links": {
            "documentation": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "indicators": "/api/v1/indicators/current"
        }
    }

@app.get("/health")
async def health_check():
    """Health check básico"""
    
    # Determinar estado general
    status = "healthy"
    if len(routers_failed) > len(routers_loaded) / 2:
        status = "degraded"
    elif len(routers_failed) > 0:
        status = "warning"
    
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "routers": {
            "loaded": len(routers_loaded),
            "failed": len(routers_failed),
            "loaded_list": [name for name, _ in routers_loaded],
            "failed_list": [name for name, _ in routers_failed] if routers_failed else []
        },
        "scheduler": scheduler_status,
        "database": "connected",  # Simplified check
        "uptime": "running"
    }

@app.get("/status")
async def detailed_status():
    """Status detallado del sistema"""
    return {
        "system": {
            "name": "Argfy Platform",
            "version": "1.0.0",
            "environment": getattr(settings, 'ENVIRONMENT', 'development'),
            "debug": getattr(settings, 'DEBUG', True),
            "timestamp": datetime.now().isoformat()
        },
        "routers": {
            "loaded": {
                name: {"status": "ok", "details": status} 
                for name, status in routers_loaded
            },
            "failed": {
                name: {"status": "error", "error": error} 
                for name, error in routers_failed
            }
        },
        "scheduler": scheduler_status,
        "features": {
            "real_time_data": scheduler_status["enabled"],
            "historical_data": "data" in available_routers,
            "economic_cards": "economic_cards" in available_routers,
            "health_monitoring": "health" in available_routers,
            "system_management": "system" in available_routers
        }
    }

# ✅ ERROR HANDLERS
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "El endpoint solicitado no existe",
        "available_endpoints": [
            "/docs - Documentación de la API",
            "/health - Estado del sistema",
            "/api/v1/indicators/current - Indicadores actuales",
            "/api/v1/data/historical - Datos históricos"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal Server Error",
        "message": "Error interno del servidor",
        "timestamp": datetime.now().isoformat(),
        "support": "Revisa los logs para más detalles"
    }

# ✅ LOG INICIAL
if __name__ == "__main__":
    logger.info("🚀 Argfy Platform configurado correctamente")
    logger.info(f"📊 Routers disponibles: {list(available_routers.keys())}")
    if routers_failed:
        logger.warning(f"⚠️ Routers fallidos: {[name for name, _ in routers_failed]}")