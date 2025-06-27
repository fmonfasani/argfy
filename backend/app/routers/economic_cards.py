# backend/app/routers/economic_cards.py
"""
Router para cards económicas con modales y gráficos históricos elegantes
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/cards", tags=["Economic Cards"])

@router.get("/", response_model=Dict[str, Any])
async def get_economic_cards(
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    limit: int = Query(8, ge=1, le=20, description="Número máximo de cards")
):
    """
    Obtiene todas las cards de indicadores económicos
    
    **Categories disponibles:**
    - exchange: Tipos de cambio
    - monetary: Variables monetarias  
    - inflation: Inflación
    - market: Mercados bursátiles
    - risk: Riesgo país
    - reserves: Reservas
    """
    try:
        from ..services.enhanced_economic_service import enhanced_economic_service
        
        async with enhanced_economic_service as service:
            cards = await service.get_economic_cards()
            
            # Filtrar por categoría si se especifica
            if category:
                cards = [card for card in cards if card.category.value == category.lower()]
            
            # Limitar resultados
            cards = cards[:limit]
            
            # Convertir a diccionarios
            cards_data = [card.to_dict() for card in cards]
            
            return {
                "status": "success",
                "data": cards_data,
                "total": len(cards_data),
                "category_filter": category,
                "timestamp": datetime.now().isoformat(),
                "categories_available": ["exchange", "monetary", "inflation", "market", "risk", "reserves"],
                "metadata": {
                    "data_sources": ["BCRA", "INDEC", "Bluelytics", "BYMA"],
                    "update_frequency": "15 minutes",
                    "real_time": True
                }
            }
            
    except Exception as e:
        logger.error(f"Error getting economic cards: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo cards: {str(e)}")

@router.get("/{card_id}/historical", response_model=Dict[str, Any])
async def get_card_historical_data(
    card_id: str,
    days: int = Query(30, ge=1, le=365, description="Días de historial"),
    chart_type: str = Query("line", description="Tipo de gráfico: line, area, bar")
):
    """
    Obtiene datos históricos elegantes para gráficos de una card específica
    
    **Tipos de gráfico disponibles:**
    - line: Línea suavizada (default)
    - area: Área con gradiente
    - bar: Barras
    """
    try:
        from ..services.enhanced_economic_service import enhanced_economic_service
        
        async with enhanced_economic_service as service:
            historical_data = await service.get_historical_data(card_id, days)
            
            if "error" in historical_data:
                raise HTTPException(status_code=404, detail=historical_data["error"])
            
            # Agregar configuración de gráfico específica
            historical_data["chart_config"]["type"] = chart_type
            historical_data["chart_config"]["responsive"] = True
            historical_data["chart_config"]["animation"] = {
                "duration": 800,
                "easing": "easeInOutQuart"
            }
            
            return {
                "status": "success",
                "indicator_id": card_id,
                "historical_data": historical_data,
                "timestamp": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting historical data for {card_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo datos históricos: {str(e)}")

@router.get("/{card_id}/summary", response_model=Dict[str, Any])
async def get_card_summary(card_id: str):
    """
    Obtiene resumen detallado de una card específica para el modal
    """
    try:
        from ..services.enhanced_economic_service import enhanced_economic_service
        
        async with enhanced_economic_service as service:
            # Obtener card actual
            cards = await service.get_economic_cards()
            card = next((c for c in cards if c.id == card_id), None)
            
            if not card:
                raise HTTPException(status_code=404, detail="Card no encontrada")
            
            # Obtener datos históricos resumidos (7 días)
            historical_summary = await service.get_historical_data(card_id, 7)
            
            return {
                "status": "success",
                "card": card.to_dict(),
                "summary": {
                    "weekly_change": historical_summary.get("statistics", {}).get("change_percent", 0),
                    "weekly_volatility": historical_summary.get("statistics", {}).get("volatility", 0),
                    "weekly_trend": historical_summary.get("statistics", {}).get("trend", "stable"),
                    "data_quality": historical_summary.get("metadata", {}).get("data_quality", "medium")
                },
                "timestamp": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting card summary for {card_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo resumen: {str(e)}")

@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_cards_data(background_tasks: BackgroundTasks):
    """
    Fuerza la actualización de todas las cards en segundo plano
    """
    try:
        async def refresh_task():
            from ..services.enhanced_economic_service import enhanced_economic_service
            async with enhanced_economic_service as service:
                await service.get_economic_cards()
                logger.info("Cards data refreshed successfully")
        
        background_tasks.add_task(refresh_task)
        
        return {
            "status": "success",
            "message": "Actualización de cards iniciada en segundo plano",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error refreshing cards: {e}")
        raise HTTPException(status_code=500, detail=f"Error actualizando cards: {str(e)}")

@router.get("/health", response_model=Dict[str, Any])
async def cards_health_check():
    """
    Health check específico para el sistema de cards
    """
    try:
        from ..services.enhanced_economic_service import enhanced_economic_service
        
        async with enhanced_economic_service as service:
            cards = await service.get_economic_cards()
            
            # Estadísticas de salud
            total_cards = len(cards)
            fresh_cards = sum(1 for card in cards if card.status.value == "fresh")
            error_cards = sum(1 for card in cards if card.status.value == "error")
            
            health_status = "healthy"
            if error_cards > total_cards * 0.3:
                health_status = "unhealthy"
            elif fresh_cards < total_cards * 0.7:
                health_status = "degraded"
            
            return {
                "status": health_status,
                "cards_total": total_cards,
                "cards_fresh": fresh_cards,
                "cards_error": error_cards,
                "freshness_percentage": (fresh_cards / total_cards) * 100 if total_cards > 0 else 0,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error in cards health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
