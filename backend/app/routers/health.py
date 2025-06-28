# backend/app/routers/health.py
"""
Router de Health Check y monitoreo del sistema
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import psutil
import logging

from ..database import get_db
from ..models import HealthCheck
from ..services.scheduler import scheduler

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check básico"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": "development"
    }

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Health check detallado con métricas del sistema"""
    try:
        # Test de base de datos
        db_healthy = True
        try:
            db.execute("SELECT 1")
        except Exception as e:
            db_healthy = False
            logger.error(f"Database health check failed: {e}")

        # Métricas del sistema
        cpu_percent = 0
        memory_percent = 0
        disk_percent = 0
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
        except ImportError:
            logger.warning("psutil not available for system metrics")
        except Exception as e:
            logger.error(f"System metrics error: {e}")

        # Estado del scheduler
        scheduler_status = scheduler.get_status() if hasattr(scheduler, 'get_status') else {"running": False}

        # Determinar estado general
        overall_status = "healthy"
        if not db_healthy:
            overall_status = "unhealthy"
        elif cpu_percent > 80 or memory_percent > 80:
            overall_status = "degraded"

        # Guardar health check en DB
        try:
            health_record = HealthCheck(
                status=overall_status,
                services=f"{{'database': {db_healthy}, 'scheduler': {scheduler_status.get('running', False)}}}",
                uptime_seconds=scheduler_status.get('uptime_seconds', 0),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                timestamp=datetime.now()
            )
            db.add(health_record)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to save health check: {e}")

        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": db_healthy,
                "scheduler": scheduler_status.get('running', False)
            },
            "system_metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent
            },
            "scheduler": scheduler_status
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@router.get("/health/history")
async def health_history(limit: int = 10, db: Session = Depends(get_db)):
    """Historial de health checks"""
    try:
        health_records = db.query(HealthCheck).order_by(
            HealthCheck.timestamp.desc()
        ).limit(limit).all()
        
        return {
            "status": "success",
            "history": [
                {
                    "timestamp": record.timestamp.isoformat(),
                    "status": record.status,
                    "uptime_seconds": record.uptime_seconds,
                    "cpu_percent": record.cpu_percent,
                    "memory_percent": record.memory_percent
                }
                for record in health_records
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get health history: {e}")
        return {"status": "error", "message": str(e)}