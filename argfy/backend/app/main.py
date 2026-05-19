# backend/app/main.py
"""
FastAPI main application con imports robustos
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import logging
import sys
from datetime import datetime

import sentry_sdk
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

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
        elif router_name == "fundamentals":
            from .routers.fundamentals import router
            return router
        elif router_name == "admin":
            from .routers.admin import router
            return router
        elif router_name == "auth":
            from .routers.auth import router
            return router
        elif router_name == "billing":
            from .routers.billing import router
            return router
        else:
            raise ImportError(f"Unknown router: {router_name}")
            
    except ImportError as e:
        msg = f"Could not load router {router_name}: {e}"
        if getattr(settings, 'ENVIRONMENT', 'development') == "production":
            raise RuntimeError(msg)
        logger.warning(f"⚠️ {msg}")
        routers_failed.append((router_name, str(e)))
        return None
    except Exception as e:
        msg = f"Error loading router {router_name}: {e}"
        if getattr(settings, 'ENVIRONMENT', 'production') == "production":
            raise RuntimeError(msg)
        logger.error(f"❌ {msg}")
        routers_failed.append((router_name, str(e)))
        return None

# ✅ CARGAR TODOS LOS ROUTERS
routers_config = [
    ("indicators", "app.routers.indicators"),
    ("fundamentals", "app.routers.fundamentals"),
    ("admin", "app.routers.admin"),
    ("auth", "app.routers.auth"),
    ("billing", "app.routers.billing"),
]

# Cargar routers disponibles
available_routers = {}
for router_name, module_path in routers_config:
    router = load_router(router_name, module_path)
    if router:
        available_routers[router_name] = router
        routers_loaded.append((router_name, "loaded"))
        logger.info(f"✅ Router {router_name} cargado exitosamente")

# ✅ ETL JOBS — register all job functions
try:
    from .jobs.refresh_prices import run as run_refresh_prices
    from .jobs.refresh_sec_filings import run as run_sec_filings
    from .jobs.recalc_ratios import run as run_recalc_ratios
    from .jobs.quality_check import run as run_quality_check
    from .scheduler import register_job, start as start_scheduler, stop as stop_scheduler

    register_job("refresh_prices", run_refresh_prices)
    register_job("refresh_sec_filings", run_sec_filings)
    register_job("recalc_ratios", run_recalc_ratios)
    register_job("quality_check", run_quality_check)
    logger.info("✅ ETL jobs registered")
    etl_ready = True
except Exception as e:
    logger.warning(f"⚠️ ETL jobs not available: {e}")
    etl_ready = False

# ✅ STARTUP/SHUTDOWN HANDLERS
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando Argfy Platform...")

    try:
        sentry_sdk.init(
            dsn=getattr(settings, 'SENTRY_DSN', ''),
            environment=getattr(settings, 'ENVIRONMENT', 'development'),
            traces_sample_rate=0.1,
        )
        logger.info("✅ Sentry initialized")

        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas de base de datos verificadas")

        from .models import PlanFeature
        PLAN_FEATURES = {
            "free":       ["screener_basic"],
            "pro":        ["screener_basic", "historical_prices", "metric_history", "csv_export"],
            "enterprise": ["screener_basic", "historical_prices", "metric_history",
                           "csv_export", "api_access", "team_invitations", "admin_etl_trigger"],
        }
        db = next(get_db())
        try:
            existing = db.query(PlanFeature).count()
            if existing == 0:
                for plan, features in PLAN_FEATURES.items():
                    for fk in features:
                        db.add(PlanFeature(plan=plan, feature_key=fk, enabled=True))
                db.commit()
                logger.info(f"✅ Plan features seeded ({sum(len(v) for v in PLAN_FEATURES.values())} rows)")
            else:
                logger.info(f"ℹ️ Plan features already seeded ({existing} rows)")
        except Exception as e:
            logger.warning(f"⚠️ Seed plans error: {e}")
        finally:
            db.close()

        if etl_ready and getattr(settings, 'ENABLE_SCHEDULER', True):
            try:
                start_scheduler()
                logger.info("🔄 APScheduler iniciado")
            except Exception as e:
                logger.warning(f"⚠️ Error iniciando APScheduler: {e}")

            try:
                from .services.scheduler import start_scheduler as start_unified_scheduler
                asyncio.create_task(start_unified_scheduler())
                logger.info("🔄 UnifiedScheduler iniciado")
            except Exception as e:
                logger.warning(f"⚠️ Error iniciando UnifiedScheduler: {e}")

        logger.info(f"📊 Routers cargados: {len(routers_loaded)}")
        logger.info(f"❌ Routers fallidos: {len(routers_failed)}")
    except Exception as e:
        logger.error(f"❌ Error en startup: {e}")

    yield

    logger.info("⏹️ Cerrando Argfy Platform...")
    if etl_ready:
        try:
            stop_scheduler()
            logger.info("🔄 APScheduler detenido")
        except Exception as e:
            logger.error(f"❌ Error deteniendo APScheduler: {e}")

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

# ✅ RATE LIMITER
from .middleware.rate_limit_middleware import limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ✅ MIDDLEWARES
from .middleware.rate_limit_middleware import RateLimitPlanMiddleware

app.add_middleware(RateLimitPlanMiddleware)

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
            "enabled": etl_ready,
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
        "scheduler": {"enabled": etl_ready},
        "database": "connected",
        "uptime": "running"
    }

@app.get("/status")
async def detailed_status():
    """Status detallado del sistema"""
    from .scheduler import scheduler as aps
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
        "scheduler": {"enabled": etl_ready, "running": aps.running},
        "features": {
            "real_time_data": etl_ready,
            "historical_data": "data" in available_routers,
            "economic_cards": "economic_cards" in available_routers,
            "health_monitoring": "health" in available_routers,
            "system_management": "system" in available_routers
        }
    }

# ✅ ERROR HANDLERS
@app.exception_handler(404)
async def not_found_handler(request, exc):
    detail = getattr(exc, "detail", None) or "El recurso solicitado no existe"
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": detail,
            "timestamp": datetime.now().isoformat(),
        },
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Error interno del servidor",
            "timestamp": datetime.now().isoformat(),
        },
    )

# ✅ LOG INICIAL
if __name__ == "__main__":
    logger.info("🚀 Argfy Platform configurado correctamente")
    logger.info(f"📊 Routers disponibles: {list(available_routers.keys())}")
    if routers_failed:
        logger.warning(f"⚠️ Routers fallidos: {[name for name, _ in routers_failed]}")