# backend/app/routers/indicators.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import EconomicIndicator, HistoricalData, NewsItem
from ..services.bcra_service import generate_demo_data, generate_historical_data, generate_demo_news
from datetime import datetime, timedelta
from typing import List, Optional
import json

router = APIRouter(prefix="/indicators", tags=["indicators"])

@router.get("/current")
async def get_current_indicators(db: Session = Depends(get_db)):
    """Obtiene indicadores económicos actuales"""
    try:
        # Verificar si tenemos datos en la DB
        indicators = db.query(EconomicIndicator).filter(
            EconomicIndicator.is_active == True
        ).all()
        
        # Si no hay datos, generar datos demo
        if not indicators:
            demo_data = generate_demo_data()
            for item in demo_data:
                indicator = EconomicIndicator(**item)
                db.add(indicator)
            db.commit()
            
            # Obtener los datos recién creados
            indicators = db.query(EconomicIndicator).filter(
                EconomicIndicator.is_active == True
            ).all()
        
        # Convertir a dict para JSON response
        indicator_data = []
        for indicator in indicators:
            indicator_data.append({
                "id": indicator.id,
                "indicator_type": indicator.indicator_type,
                "value": indicator.value,
                "date": indicator.date.isoformat(),
                "source": indicator.source,
                "is_active": indicator.is_active
            })
        
        return {
            "data": indicator_data,
            "timestamp": datetime.utcnow().isoformat(),
            "count": len(indicator_data),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching indicators: {str(e)}")

@router.get("/historical/{indicator_type}")
async def get_historical_data(
    indicator_type: str, 
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obtiene datos históricos de un indicador específico"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Buscar datos históricos en la DB
        data = db.query(HistoricalData).filter(
            HistoricalData.indicator_id == indicator_type,
            HistoricalData.date >= start_date
        ).order_by(HistoricalData.date.asc()).all()
        
        # Si no hay datos, generar datos demo
        if not data:
            historical_demo = generate_historical_data(indicator_type, days)
            for item in historical_demo:
                hist_data = HistoricalData(**item)
                db.add(hist_data)
            db.commit()
            
            # Obtener los datos recién creados
            data = db.query(HistoricalData).filter(
                HistoricalData.indicator_id == indicator_type,
                HistoricalData.date >= start_date
            ).order_by(HistoricalData.date.asc()).all()
        
        # Convertir a formato para gráficos
        chart_data = []
        for item in data:
            chart_data.append({
                "date": item.date.strftime("%Y-%m-%d"),
                "value": item.value,
                "source": item.source
            })
        
        return {
            "indicator": indicator_type,
            "data": chart_data,
            "period": f"{days} days",
            "count": len(chart_data),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")

@router.get("/news")
async def get_news(
    limit: int = Query(6, ge=1, le=20),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtiene noticias económicas"""
    try:
        # Verificar si tenemos noticias en la DB
        query = db.query(NewsItem)
        
        if category:
            query = query.filter(NewsItem.category == category.upper())
            
        news = query.order_by(NewsItem.published_at.desc()).limit(limit).all()
        
        # Si no hay noticias, generar datos demo
        if not news:
            demo_news = generate_demo_news()
            for item in demo_news:
                news_item = NewsItem(**item)
                db.add(news_item)
            db.commit()
            
            # Obtener las noticias recién creadas
            query = db.query(NewsItem)
            if category:
                query = query.filter(NewsItem.category == category.upper())
            news = query.order_by(NewsItem.published_at.desc()).limit(limit).all()
        
        # Convertir a dict
        news_data = []
        for item in news:
            news_data.append({
                "id": item.id,
                "title": item.title,
                "summary": item.summary,
                "category": item.category,
                "source": item.source,
                "published_at": item.published_at.isoformat(),
                "is_featured": item.is_featured
            })
        
        return {
            "data": news_data,
            "count": len(news_data),
            "category": category,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@router.get("/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Obtiene resumen completo para el dashboard"""
    try:
        # Obtener indicadores actuales
        indicators_response = await get_current_indicators(db)
        
        # Obtener noticias destacadas
        news_response = await get_news(limit=3, db=db)
        
        # Crear resumen estructurado
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "indicators": {
                "count": indicators_response["count"],
                "data": indicators_response["data"]
            },
            "news": {
                "count": news_response["count"], 
                "featured": news_response["data"]
            },
            "status": "success"
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

# Endpoint para refresh manual de datos
@router.post("/refresh")
async def refresh_indicators(db: Session = Depends(get_db)):
    """Actualiza todos los indicadores con nuevos datos"""
    try:
        # Desactivar indicadores existentes
        db.query(EconomicIndicator).update({"is_active": False})
        
        # Generar nuevos datos
        demo_data = generate_demo_data()
        for item in demo_data:
            indicator = EconomicIndicator(**item)
            db.add(indicator)
        
        db.commit()
        
        return {
            "message": "Indicators refreshed successfully",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error refreshing data: {str(e)}")