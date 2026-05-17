# backend/app/routers/data.py
"""
Router para endpoints de datos históricos y procesamiento
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

# Imports con manejo de errores
try:
    from ..database import get_db
    from ..models import EconomicIndicator, HistoricalData
except ImportError:
    # Fallback para imports relativos
    from app.database import get_db
    from app.models import EconomicIndicator, HistoricalData

logger = logging.getLogger(__name__)

# ✅ CREAR EL ROUTER (esto es lo que faltaba)
router = APIRouter(prefix="/api/v1/data", tags=["Historical Data"])

@router.get("/")
async def get_data_info():
    """Endpoint básico para verificar que el router funciona"""
    return {
        "message": "Data Router funcionando correctamente",
        "timestamp": datetime.now().isoformat(),
        "status": "active",
        "endpoints": [
            "GET /api/v1/data/historical",
            "GET /api/v1/data/timeseries/{indicator}",
            "GET /api/v1/data/export/{format}"
        ]
    }

@router.get("/historical")
async def get_historical_data(
    indicator: Optional[str] = Query(None, description="Tipo de indicador"),
    days: int = Query(30, description="Días hacia atrás", ge=1, le=365),
    limit: int = Query(100, description="Máximo de registros", ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Obtener datos históricos con filtros"""
    try:
        query = db.query(EconomicIndicator)
        
        # Filtrar por indicador si se especifica
        if indicator:
            query = query.filter(EconomicIndicator.indicator_type == indicator)
        
        # Filtrar por fecha
        cutoff_date = datetime.now() - timedelta(days=days)
        query = query.filter(EconomicIndicator.date >= cutoff_date)
        
        # Ordenar por fecha descendente y limitar
        query = query.order_by(EconomicIndicator.date.desc()).limit(limit)
        
        results = query.all()
        
        # Formatear datos
        data_points = []
        for result in results:
            data_points.append({
                "id": result.id,
                "indicator_type": result.indicator_type,
                "value": result.value,
                "date": result.date.isoformat(),
                "source": result.source,
                "is_active": result.is_active
            })
        
        return {
            "status": "success",
            "filter": {
                "indicator": indicator,
                "days": days,
                "limit": limit
            },
            "data": data_points,
            "count": len(data_points),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo datos históricos: {str(e)}")

@router.get("/timeseries/{indicator}")
async def get_timeseries_data(
    indicator: str,
    period: str = Query("daily", description="Período: daily, weekly, monthly"),
    days: int = Query(30, description="Días de historial", ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obtener serie temporal de un indicador específico"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Buscar datos del indicador
        data = db.query(EconomicIndicator).filter(
            EconomicIndicator.indicator_type == indicator,
            EconomicIndicator.date >= cutoff_date
        ).order_by(EconomicIndicator.date.asc()).all()
        
        if not data:
            raise HTTPException(
                status_code=404, 
                detail=f"No data found for indicator '{indicator}'"
            )
        
        # Procesar según el período
        timeseries = []
        for record in data:
            timeseries.append({
                "date": record.date.isoformat(),
                "value": record.value,
                "source": record.source
            })
        
        # Calcular estadísticas básicas
        values = [record.value for record in data if record.value is not None]
        statistics = {}
        
        if values:
            statistics = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "average": sum(values) / len(values),
                "latest": values[-1] if values else None,
                "change": values[-1] - values[0] if len(values) > 1 else 0
            }
        
        return {
            "status": "success",
            "indicator": indicator,
            "period": period,
            "days": days,
            "timeseries": timeseries,
            "statistics": statistics,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting timeseries for {indicator}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/{format}")
async def export_data(
    format: str,
    indicator: Optional[str] = Query(None, description="Indicador específico"),
    days: int = Query(30, description="Días de datos", ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Exportar datos en diferentes formatos"""
    
    # Validar formato
    if format.lower() not in ["json", "csv"]:
        raise HTTPException(
            status_code=400, 
            detail="Format must be 'json' or 'csv'"
        )
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        query = db.query(EconomicIndicator).filter(
            EconomicIndicator.date >= cutoff_date
        )
        
        if indicator:
            query = query.filter(EconomicIndicator.indicator_type == indicator)
        
        data = query.order_by(EconomicIndicator.date.desc()).all()
        
        if format.lower() == "json":
            export_data = []
            for record in data:
                export_data.append({
                    "indicator_type": record.indicator_type,
                    "value": record.value,
                    "date": record.date.isoformat(),
                    "source": record.source
                })
            
            return {
                "status": "success",
                "format": "json",
                "data": export_data,
                "count": len(export_data)
            }
        
        elif format.lower() == "csv":
            # Para CSV, devolver como texto plano
            from fastapi.responses import PlainTextResponse
            
            csv_lines = ["indicator_type,value,date,source"]
            for record in data:
                csv_lines.append(
                    f"{record.indicator_type},{record.value},{record.date.isoformat()},{record.source}"
                )
            
            csv_content = "\n".join(csv_lines)
            
            return PlainTextResponse(
                content=csv_content,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=indicators_{days}days.csv"}
            )
    
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_data_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas generales de los datos"""
    try:
        from sqlalchemy import func, distinct
        
        # Estadísticas básicas
        total_records = db.query(EconomicIndicator).count()
        active_records = db.query(EconomicIndicator).filter(
            EconomicIndicator.is_active == True
        ).count()
        
        # Indicadores únicos
        unique_indicators = db.query(
            distinct(EconomicIndicator.indicator_type)
        ).count()
        
        # Fuentes de datos
        sources = db.query(
            EconomicIndicator.source,
            func.count(EconomicIndicator.id).label('count')
        ).group_by(EconomicIndicator.source).all()
        
        # Datos por día (últimos 7 días)
        last_week = datetime.now() - timedelta(days=7)
        daily_stats = db.query(
            func.date(EconomicIndicator.date).label('day'),
            func.count(EconomicIndicator.id).label('count')
        ).filter(
            EconomicIndicator.date >= last_week
        ).group_by(func.date(EconomicIndicator.date)).all()
        
        return {
            "status": "success",
            "statistics": {
                "total_records": total_records,
                "active_records": active_records,
                "unique_indicators": unique_indicators,
                "sources": {source.source: source.count for source in sources},
                "daily_activity": [
                    {"date": str(stat.day), "records": stat.count}
                    for stat in daily_stats
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting data stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup")
async def cleanup_old_data(
    days: int = Query(90, description="Días para mantener", ge=30),
    dry_run: bool = Query(True, description="Solo simular, no borrar"),
    db: Session = Depends(get_db)
):
    """Limpiar datos antiguos"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Contar registros que se borrarían
        old_records = db.query(EconomicIndicator).filter(
            EconomicIndicator.date < cutoff_date,
            EconomicIndicator.is_active == False
        ).count()
        
        if dry_run:
            return {
                "status": "success",
                "message": "Dry run - no data deleted",
                "would_delete": old_records,
                "cutoff_date": cutoff_date.isoformat()
            }
        
        # Borrar realmente
        deleted = db.query(EconomicIndicator).filter(
            EconomicIndicator.date < cutoff_date,
            EconomicIndicator.is_active == False
        ).delete()
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Deleted {deleted} old records",
            "deleted_count": deleted,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error cleaning up data: {e}")
        raise HTTPException(status_code=500, detail=str(e))