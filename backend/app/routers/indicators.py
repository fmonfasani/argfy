# backend/app/routers/indicators.py
"""
Router principal de indicadores económicos
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime, timedelta

from ..database import get_db
from ..models import EconomicIndicator, HistoricalData
from ..services.bcra_service import bcra_service
from ..config.indicators_mapping import ALL_INDICATORS

router = APIRouter()

@router.get("/indicators/current")
async def get_current_indicators(db: Session = Depends(get_db)):
    """Obtener indicadores económicos actuales"""
    try:
        # Obtener últimos indicadores de cada tipo
        subquery = db.query(
            EconomicIndicator.indicator_type,
            func.max(EconomicIndicator.date).label('max_date')
        ).filter(
            EconomicIndicator.is_active == True
        ).group_by(EconomicIndicator.indicator_type).subquery()

        current_indicators = db.query(EconomicIndicator).join(
            subquery,
            (EconomicIndicator.indicator_type == subquery.c.indicator_type) &
            (EconomicIndicator.date == subquery.c.max_date)
        ).all()

        # Formatear respuesta
        indicators_data = []
        for indicator in current_indicators:
            indicators_data.append({
                "indicator_type": indicator.indicator_type,
                "value": indicator.value,
                "source": indicator.source,
                "date": indicator.date.isoformat(),
                "unit": indicator.unit,
                "label": indicator.label,
                "category": indicator.category
            })

        return {
            "status": "success",
            "data": indicators_data,
            "timestamp": datetime.now().isoformat(),
            "count": len(indicators_data)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching indicators: {str(e)}")

@router.get("/indicators/{indicator_type}")
async def get_indicator_by_type(
    indicator_type: str,
    db: Session = Depends(get_db)
):
    """Obtener un indicador específico por tipo"""
    try:
        indicator = db.query(EconomicIndicator).filter(
            EconomicIndicator.indicator_type == indicator_type,
            EconomicIndicator.is_active == True
        ).order_by(EconomicIndicator.date.desc()).first()

        if not indicator:
            raise HTTPException(
                status_code=404, 
                detail=f"Indicator '{indicator_type}' not found"
            )

        return {
            "status": "success",
            "indicator": {
                "indicator_type": indicator.indicator_type,
                "value": indicator.value,
                "source": indicator.source,
                "date": indicator.date.isoformat(),
                "unit": indicator.unit,
                "label": indicator.label,
                "category": indicator.category
            },
            "metadata": ALL_INDICATORS.get(indicator_type, {})
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/{indicator_type}/historical")
async def get_historical_data(
    indicator_type: str,
    days: int = Query(30, description="Días de historial", ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obtener datos históricos de un indicador"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Buscar en HistoricalData primero
        historical_data = db.query(HistoricalData).filter(
            HistoricalData.indicator_type == indicator_type,
            HistoricalData.date >= cutoff_date
        ).order_by(HistoricalData.date.asc()).all()

        # Si no hay datos históricos, buscar en EconomicIndicator
        if not historical_data:
            historical_data = db.query(EconomicIndicator).filter(
                EconomicIndicator.indicator_type == indicator_type,
                EconomicIndicator.date >= cutoff_date
            ).order_by(EconomicIndicator.date.asc()).all()

        if not historical_data:
            raise HTTPException(
                status_code=404, 
                detail=f"No historical data found for '{indicator_type}'"
            )

        # Formatear datos
        data_points = []
        for record in historical_data:
            data_points.append({
                "date": record.date.isoformat(),
                "value": record.value,
                "source": record.source
            })

        return {
            "status": "success",
            "indicator_type": indicator_type,
            "period": f"{days} days",
            "data_points": len(data_points),
            "data": data_points
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/indicators/refresh")
async def refresh_indicators(background_tasks: BackgroundTasks):
    """Forzar actualización de indicadores"""
    
    async def update_task():
        try:
            async with bcra_service as service:
                data = await service.get_current_indicators()
                
                if data.get("indicators"):
                    db = next(get_db())
                    try:
                        for key, indicator_data in data["indicators"].items():
                            # Desactivar indicadores anteriores
                            db.query(EconomicIndicator).filter(
                                EconomicIndicator.indicator_type == key,
                                EconomicIndicator.is_active == True
                            ).update({"is_active": False})
                            
                            # Crear nuevo indicador
                            new_indicator = EconomicIndicator(
                                indicator_type=key,
                                value=indicator_data["value"],
                                source=indicator_data["source"],
                                unit=indicator_data.get("unit"),
                                label=indicator_data.get("label"),
                                category=indicator_data.get("category"),
                                date=datetime.now(),
                                is_active=True
                            )
                            db.add(new_indicator)
                        
                        db.commit()
                        print("✅ Indicators refreshed successfully")
                    finally:
                        db.close()
                        
        except Exception as e:
            print(f"❌ Error refreshing indicators: {e}")
    
    background_tasks.add_task(update_task)
    
    return {
        "status": "success",
        "message": "Actualización iniciada en segundo plano",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/indicators/search")
async def search_indicators(
    q: str = Query(..., description="Término de búsqueda"),
    source: Optional[str] = Query(None, description="Filtrar por fuente"),
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    db: Session = Depends(get_db)
):
    """Buscar indicadores"""
    try:
        query = db.query(EconomicIndicator).filter(
            EconomicIndicator.is_active == True
        )
        
        # Filtro de búsqueda en label o indicator_type
        search_term = f"%{q.lower()}%"
        query = query.filter(
            (func.lower(EconomicIndicator.label).like(search_term)) |
            (func.lower(EconomicIndicator.indicator_type).like(search_term))
        )
        
        # Filtros adicionales
        if source:
            query = query.filter(EconomicIndicator.source == source.upper())
        
        if category:
            query = query.filter(EconomicIndicator.category == category.lower())
        
        # Obtener solo el más reciente de cada tipo
        subquery = query.with_entities(
            EconomicIndicator.indicator_type,
            func.max(EconomicIndicator.date).label('max_date')
        ).group_by(EconomicIndicator.indicator_type).subquery()
        
        results = db.query(EconomicIndicator).join(
            subquery,
            (EconomicIndicator.indicator_type == subquery.c.indicator_type) &
            (EconomicIndicator.date == subquery.c.max_date)
        ).limit(20).all()
        
        return {
            "status": "success",
            "query": q,
            "filters": {"source": source, "category": category},
            "results": [
                {
                    "indicator_type": r.indicator_type,
                    "label": r.label,
                    "value": r.value,
                    "source": r.source,
                    "category": r.category,
                    "date": r.date.isoformat()
                }
                for r in results
            ],
            "count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/stats")
async def get_indicators_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas de indicadores"""
    try:
        total_indicators = db.query(EconomicIndicator).filter(
            EconomicIndicator.is_active == True
        ).count()
        
        sources_stats = db.query(
            EconomicIndicator.source,
            func.count(EconomicIndicator.id).label('count')
        ).filter(
            EconomicIndicator.is_active == True
        ).group_by(EconomicIndicator.source).all()
        
        categories_stats = db.query(
            EconomicIndicator.category,
            func.count(EconomicIndicator.id).label('count')
        ).filter(
            EconomicIndicator.is_active == True
        ).group_by(EconomicIndicator.category).all()
        
        return {
            "status": "success",
            "total_indicators": total_indicators,
            "by_source": {stat.source: stat.count for stat in sources_stats if stat.source},
            "by_category": {stat.category: stat.count for stat in categories_stats if stat.category},
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))