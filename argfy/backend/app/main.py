# backend/app/main.py
"""FastAPI main application."""

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from .database import engine, Base, get_db
    from .models import EconomicIndicator, HistoricalData
    from .config import settings
except ImportError as e:
    logger.error(f"Error importing core modules: {e}")
    sys.exit(1)

routers_loaded: list[tuple[str, str]] = []
routers_failed: list[tuple[str, str]] = []


def load_router(router_name: str):
    try:
        if router_name == "indicators":
            from .routers.indicators import router
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
        logger.warning(f"Router {router_name} skipped: {msg}")
        routers_failed.append((router_name, str(e)))
        return None
    except Exception as e:
        msg = f"Error loading router {router_name}: {e}"
        if getattr(settings, 'ENVIRONMENT', 'production') == "production":
            raise RuntimeError(msg)
        logger.error(f"Router {router_name} error: {msg}")
        routers_failed.append((router_name, str(e)))
        return None


routers_config = [
    "indicators",
    "fundamentals",
    "admin",
    "auth",
    "billing",
]

available_routers = {}
for router_name in routers_config:
    router = load_router(router_name)
    if router:
        available_routers[router_name] = router
        routers_loaded.append((router_name, "loaded"))
        logger.info(f"Router {router_name} loaded")

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
    logger.info("ETL jobs registered")
    etl_ready = True
except Exception as e:
    logger.warning(f"ETL jobs not available: {e}")
    etl_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Argfy Platform...")

    try:
        sentry_sdk.init(
            dsn=getattr(settings, 'SENTRY_DSN', ''),
            environment=getattr(settings, 'ENVIRONMENT', 'development'),
            traces_sample_rate=0.1,
        )
        logger.info("Sentry initialized")

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified")

        from .models import PlanFeature
        PLAN_FEATURES = {
            "free": ["screener_basic"],
            "pro": ["screener_basic", "historical_prices", "metric_history", "csv_export"],
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
                logger.info(f"Plan features seeded ({sum(len(v) for v in PLAN_FEATURES.values())} rows)")
            else:
                logger.info(f"Plan features already seeded ({existing} rows)")
        except Exception as e:
            logger.warning(f"Seed plans error: {e}")
        finally:
            db.close()

        if etl_ready and getattr(settings, 'ENABLE_SCHEDULER', True):
            try:
                start_scheduler()
                logger.info("APScheduler started")
            except Exception as e:
                logger.warning(f"APScheduler error: {e}")

            try:
                from .services.scheduler import start_scheduler as start_unified_scheduler
                asyncio.create_task(start_unified_scheduler())
                logger.info("UnifiedScheduler started")
            except Exception as e:
                logger.warning(f"UnifiedScheduler error: {e}")

        logger.info(f"Routers loaded: {len(routers_loaded)}")
        logger.info(f"Routers failed: {len(routers_failed)}")
    except Exception as e:
        logger.error(f"Startup error: {e}")

    yield

    logger.info("Shutting down Argfy Platform...")
    if etl_ready:
        try:
            stop_scheduler()
            logger.info("APScheduler stopped")
        except Exception as e:
            logger.error(f"APScheduler shutdown error: {e}")


app = FastAPI(
    title="Argfy Platform API",
    description="API REST para datos económicos argentinos y fundamentos de CEDEARs.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

from .middleware.rate_limit_middleware import limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from .middleware.rate_limit_middleware import RateLimitPlanMiddleware
app.add_middleware(RateLimitPlanMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, 'CORS_ORIGINS', ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router_name, router in available_routers.items():
    try:
        app.include_router(router)
        logger.info(f"Router {router_name} included")
    except Exception as e:
        logger.error(f"Router {router_name} include error: {e}")
        routers_failed.append((router_name, f"Include error: {str(e)}"))


@app.get("/")
async def root():
    return {
        "name": "Argfy Platform API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "routers": {
            "loaded": [name for name, _ in routers_loaded],
            "failed": [name for name, _ in routers_failed],
            "total_loaded": len(routers_loaded),
            "total_failed": len(routers_failed),
        },
        "scheduler": {"enabled": etl_ready},
        "links": {
            "documentation": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "indicators": "/api/v1/indicators/current",
        },
    }


@app.get("/health")
async def health_check():
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
            "failed_list": [name for name, _ in routers_failed] if routers_failed else [],
        },
        "scheduler": {"enabled": etl_ready},
        "database": "connected",
    }


@app.exception_handler(404)
async def not_found_handler(request, exc):
    detail = getattr(exc, "detail", None) or "El recurso solicitado no existe"
    return JSONResponse(
        status_code=404,
        content={"error": "Not Found", "message": detail, "timestamp": datetime.now().isoformat()},
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": "Error interno del servidor", "timestamp": datetime.now().isoformat()},
    )


if __name__ == "__main__":
    logger.info(f"Routers available: {list(available_routers.keys())}")
    if routers_failed:
        logger.warning(f"Failed routers: {[name for name, _ in routers_failed]}")
