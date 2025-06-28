# backend/app/main.py
"""
FastAPI Application Principal – limpio y compatible
"""

from __future__ import annotations

import asyncio
import logging
import logging.config
from contextlib import asynccontextmanager
from datetime import datetime
from app.utils.emoji_log import e   

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from .config import settings
from .database import Base, engine, get_db
from .routers import health, indicators, system
from .services.scheduler import scheduler, start_scheduler, stop_scheduler

# --- IMPORTS CORREGIDOS (clases, no módulos) ------------------------------
from .middleware.logging_middleware import LoggingMiddleware      # ← cambio
from .middleware.rate_limit_middleware import RateLimitMiddleware  # ← cambio

# ------------------------------------------------------------------------- #
# Logging
logging.config.dictConfig(settings.log_config)
logger = logging.getLogger("argfy.main")

# -------------------------- Lifespan ------------------------------------- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Argfy Platform...")
    try:
        # 1. Crear tablas
        logger.info("📦 Creating database tables...")
        Base.metadata.create_all(bind=engine)

        # 2. Datos demo
        if settings.DEMO_MODE:
            await initialize_demo_data()

        # 3. Scheduler
        if settings.ENABLE_SCHEDULER:
            logger.info("⏰ Starting background scheduler...")
            asyncio.create_task(start_scheduler())

        logger.info("✅ Argfy Platform started successfully")
        yield

    except Exception as exc:
        logger.exception("❌ Failed to start application: %s", exc)
        raise

    # --- shutdown ----
    logger.info("🛑 Shutting down Argfy Platform...")
    if settings.ENABLE_SCHEDULER:
        stop_scheduler()
    logger.info("✅ Argfy Platform shut down successfully")


# ---------------------- FastAPI instancia -------------------------------- #
app = FastAPI(
    title="Argfy Platform API",
    description=(
        "## 🇦🇷 API de Datos Económicos Argentinos\n\n"
        "Plataforma consolidada para acceder a indicadores económicos "
        "argentinos en tiempo real."
    ),
    version="1.0.0",
    contact={"name": "Argfy Team", "email": "contact@argfy.com", "url": "https://argfy.com"},
    license_info={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)

# ------------------------- MIDDLEWARE ------------------------------------ #
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],                     # ← “*” para todos
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time"],
)

if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["argfy.com", "*.argfy.com", "api.argfy.com"],
    )

app.add_middleware(RateLimitMiddleware)   # ← clase, no módulo
app.add_middleware(LoggingMiddleware)     # ← clase, no módulo

# --------------------------- ROUTERS ------------------------------------- #
app.include_router(indicators.router, prefix="/api/v1", tags=["Indicadores"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(system.router, prefix="/api/v1", tags=["Sistema"])

# --------------------------- ENDPOINTS ----------------------------------- #
@app.get("/", summary="Información de la API")
async def root():
    return {
        "name": "Argfy Platform API",
        "version": app.version,
        "status": "operational",
        "demo_mode": settings.DEMO_MODE,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/ping", summary="Health Check simple")
async def ping():
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}


# ---------------------- ERROR HANDLERS ----------------------------------- #
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path,
            }
        },
    )


@app.exception_handler(500)
async def internal_error(request: Request, exc: Exception):
    logger.exception("Internal server error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path,
            }
        },
    )


# ---------------------- CUSTOM OPENAPI ----------------------------------- #
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema["info"]["x-logo"] = {"url": "https://argfy.com/logo.png"}
    schema["servers"] = [
        {"url": "https://api.argfy.com", "description": "Prod"},
        {"url": "http://localhost:8000", "description": "Dev"},
    ]
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi

# ------------------- DEMO DATA INIT -------------------------------------- #
async def initialize_demo_data():
    try:
        from .models import EconomicIndicator

        db = next(get_db())
        if db.query(EconomicIndicator).count() == 0:
            logger.info("📊 Initializing demo data...")
            db.add_all(
                [
                    EconomicIndicator(
                        indicator_type="usd_minorista",
                        value=1195.0,
                        source="DEMO",
                        unit="ARS",
                        label="USD Minorista",
                    ),
                    # … otros demo
                ]
            )
            db.commit()
            logger.info("✅ Demo data ready")
        db.close()
    except Exception as exc:
        logger.exception("❌ Failed to init demo data: %s", exc)


# -------------------- CLI ------------------------------------------------ #
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD and settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )
