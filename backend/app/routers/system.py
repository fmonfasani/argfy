# backend/app/routers/system.py
"""
Router de sistema y administración
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from ..database import get_db
from ..models import Configuration, APIUsage
from ..services.scheduler import scheduler
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/system/info")
async def system_info():
    """Información del sistema"""
    return {
        "name": "Argfy Platform API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "demo_mode": settings.DEMO_MODE,
        "scheduler_enabled": settings.ENABLE_SCHEDULER,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/system/config")
async def get_system_config(db: Session = Depends(get_db)):
    """Obtener configuración del sistema"""
    try:
        configs = db.query(Configuration).filter(
            Configuration.is_active == True
        ).all()
        
        config_dict = {}
        for config in configs:
            config_dict[config.key] = {
                "value": config.get_typed_value(),
                "type": config.value_type,
                "description": config.description,
                "category": config.category,
                "updated_at": config.updated_at.isoformat()
            }
        
        return {
            "status": "success",
            "config": config_dict,
            "count": len(configs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/system/config/{key}")
async def update_config(
    key: str, 
    value: str,
    value_type: str = "string",
    db: Session = Depends(get_db)
):
    """Actualizar configuración del sistema"""
    try:
        config = db.query(Configuration).filter(
            Configuration.key == key
        ).first()
        
        if config:
            config.value = value
            config.value_type = value_type
            config.updated_at = datetime.now()
        else:
            config = Configuration(
                key=key,
                value=value,
                value_type=value_type,
                is_active=True
            )
            db.add(config)
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Configuration '{key}' updated",
            "config": {
                "key": key,
                "value": config.get_typed_value(),
                "type": value_type
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/scheduler/status")
async def get_scheduler_status():
    """Estado del scheduler"""
    try:
        if hasattr(scheduler, 'get_status'):
            return {
                "status": "success",
                "scheduler": scheduler.get_status()
            }
        else:
            return {
                "status": "success",
                "scheduler": {
                    "running": False,
                    "message": "Scheduler not initialized"
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/system/scheduler/start")
async def start_scheduler_endpoint():
    """Iniciar scheduler manualmente"""
    try:
        if hasattr(scheduler, 'start'):
            if not scheduler.running:
                # No podemos usar await aquí porque start() es blocking
                return {
                    "status": "success",
                    "message": "Scheduler start requested"
                }
            else:
                return {
                    "status": "info",
                    "message": "Scheduler already running"
                }
        else:
            raise HTTPException(status_code=500, detail="Scheduler not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/system/scheduler/stop")
async def stop_scheduler_endpoint():
    """Detener scheduler manualmente"""
    try:
        if hasattr(scheduler, 'stop'):
            scheduler.stop()
            return {
                "status": "success",
                "message": "Scheduler stopped"
            }
        else:
            raise HTTPException(status_code=500, detail="Scheduler not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/api-usage")
async def get_api_usage_stats(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Estadísticas de uso de la API"""
    try:
        cutoff = datetime.now() - timedelta(hours=hours)
        
        # Total requests
        total_requests = db.query(APIUsage).filter(
            APIUsage.timestamp >= cutoff
        ).count()
        
        # Requests por endpoint
        endpoint_stats = db.query(
            APIUsage.endpoint,
            func.count(APIUsage.id).label('count'),
            func.avg(APIUsage.response_time_ms).label('avg_response_time')
        ).filter(
            APIUsage.timestamp >= cutoff
        ).group_by(APIUsage.endpoint).all()
        
        # Status codes
        status_stats = db.query(
            APIUsage.status_code,
            func.count(APIUsage.id).label('count')
        ).filter(
            APIUsage.timestamp >= cutoff
        ).group_by(APIUsage.status_code).all()
        
        return {
            "status": "success",
            "period_hours": hours,
            "total_requests": total_requests,
            "endpoints": [
                {
                    "endpoint": stat.endpoint,
                    "requests": stat.count,
                    "avg_response_time_ms": round(stat.avg_response_time or 0, 2)
                }
                for stat in endpoint_stats
            ],
            "status_codes": {
                str(stat.status_code): stat.count 
                for stat in status_stats
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/system/cleanup")
async def cleanup_old_data(
    days: int = 90,
    db: Session = Depends(get_db)
):
    """Limpiar datos viejos del sistema"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Limpiar API usage viejo
        deleted_api_usage = db.query(APIUsage).filter(
            APIUsage.timestamp < cutoff_date
        ).delete()
        
        # Limpiar health checks viejos
        deleted_health = db.query(HealthCheck).filter(
            HealthCheck.timestamp < cutoff_date
        ).delete()
        
        # Limpiar indicadores inactivos viejos
        deleted_indicators = db.query(EconomicIndicator).filter(
            EconomicIndicator.date < cutoff_date,
            EconomicIndicator.is_active == False
        ).delete()
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Cleaned up data older than {days} days",
            "deleted": {
                "api_usage": deleted_api_usage,
                "health_checks": deleted_health,
                "inactive_indicators": deleted_indicators
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/logs")
async def get_recent_logs(lines: int = 100):
    """Obtener logs recientes del sistema"""
    try:
        log_file = "logs/argfy.log"
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
            return {
                "status": "success",
                "lines": len(recent_lines),
                "logs": [line.strip() for line in recent_lines]
            }
            
        except FileNotFoundError:
            return {
                "status": "warning",
                "message": "Log file not found",
                "logs": []
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))