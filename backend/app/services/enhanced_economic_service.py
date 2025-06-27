# backend/app/services/enhanced_economic_service.py
"""
Servicio económico mejorado que integra todas las fuentes de datos
con cards dinámicas y modales con gráficos históricos elegantes
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import logging
import json
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class IndicatorCategory(Enum):
    """Categorías de indicadores económicos"""
    EXCHANGE = "exchange"
    MONETARY = "monetary" 
    INFLATION = "inflation"
    MARKET = "market"
    RISK = "risk"
    RESERVES = "reserves"

class IndicatorStatus(Enum):
    """Estado de actualización del indicador"""
    FRESH = "fresh"      # < 15 min
    RECENT = "recent"    # < 1 hora
    STALE = "stale"      # > 1 hora
    ERROR = "error"      # Error al obtener

@dataclass
class EconomicCard:
    """Estructura para cards de indicadores económicos"""
    id: str
    title: str
    value: float
    previous_value: Optional[float]
    unit: str
    category: IndicatorCategory
    status: IndicatorStatus
    change_percent: Optional[float]
    change_absolute: Optional[float]
    trend: str  # "up", "down", "stable"
    last_updated: datetime
    source: str
    description: str
    icon: str
    color_theme: str  # "green", "red", "blue", "yellow", "purple"
    sparkline_data: List[float]  # Últimos 10 valores para mini gráfico
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para JSON"""
        return {
            "id": self.id,
            "title": self.title,
            "value": self.value,
            "previous_value": self.previous_value,
            "unit": self.unit,
            "category": self.category.value,
            "status": self.status.value,
            "change_percent": self.change_percent,
            "change_absolute": self.change_absolute,
            "trend": self.trend,
            "last_updated": self.last_updated.isoformat(),
            "source": self.source,
            "description": self.description,
            "icon": self.icon,
            "color_theme": self.color_theme,
            "sparkline_data": self.sparkline_data,
            "is_fresh": self.status == IndicatorStatus.FRESH,
            "minutes_since_update": int((datetime.now() - self.last_updated).total_seconds() / 60)
        }

class EnhancedEconomicService:
    """Servicio económico mejorado con cards y gráficos"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 5 minutos
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_economic_cards(self) -> List[EconomicCard]:
        """Obtiene todas las cards de indicadores económicos"""
        cards = []
        
        # Por ahora retornar cards demo - TODO: integrar con servicios reales
        import random
        
        demo_cards = [
            {
                "id": "usd_oficial",
                "title": "USD Oficial",
                "value": round(987.5 + random.uniform(-10, 10), 2),
                "category": IndicatorCategory.EXCHANGE,
                "icon": "💵",
                "color_theme": "blue",
                "description": "Cotización oficial USD/ARS del BCRA"
            },
            {
                "id": "usd_blue",
                "title": "Dólar Blue",
                "value": round(1180.0 + random.uniform(-20, 20), 2),
                "category": IndicatorCategory.EXCHANGE,
                "icon": "💙",
                "color_theme": "purple",
                "description": "Cotización paralela del dólar en cuevas"
            },
            {
                "id": "reservas_bcra",
                "title": "Reservas BCRA",
                "value": round(21500.0 + random.uniform(-500, 500), 2),
                "category": IndicatorCategory.RESERVES,
                "icon": "🏦",
                "color_theme": "blue",
                "description": "Reservas internacionales en USD millones"
            },
            {
                "id": "tasa_bcra",
                "title": "Tasa BCRA",
                "value": round(118.0 + random.uniform(-2, 2), 1),
                "category": IndicatorCategory.MONETARY,
                "icon": "📊",
                "color_theme": "red",
                "description": "Tasa de política monetaria del BCRA"
            },
            {
                "id": "inflacion",
                "title": "Inflación",
                "value": round(4.2 + random.uniform(-0.5, 0.5), 1),
                "category": IndicatorCategory.INFLATION,
                "icon": "📉",
                "color_theme": "red",
                "description": "Inflación mensual INDEC"
            },
            {
                "id": "riesgo_pais",
                "title": "Riesgo País",
                "value": round(1642.0 + random.uniform(-50, 50)),
                "category": IndicatorCategory.RISK,
                "icon": "⚠️",
                "color_theme": "yellow",
                "description": "EMBI+ Argentina en puntos básicos"
            },
            {
                "id": "merval",
                "title": "Merval",
                "value": round(1456234.0 + random.uniform(-10000, 10000)),
                "category": IndicatorCategory.MARKET,
                "icon": "📊",
                "color_theme": "green",
                "description": "Índice bursátil Merval"
            }
        ]
        
        for card_data in demo_cards:
            # Generar sparkline demo
            sparkline = []
            base_value = card_data["value"]
            for i in range(10):
                variation = random.uniform(-0.02, 0.02)
                sparkline.append(round(base_value * (1 + variation), 2))
            
            card = EconomicCard(
                id=card_data["id"],
                title=card_data["title"],
                value=card_data["value"],
                previous_value=card_data["value"] * (1 + random.uniform(-0.01, 0.01)),
                unit=self._get_unit_for_indicator(card_data["id"]),
                category=card_data["category"],
                status=IndicatorStatus.FRESH,
                change_percent=random.uniform(-2, 2),
                change_absolute=random.uniform(-10, 10),
                trend=random.choice(["up", "down", "stable"]),
                last_updated=datetime.now(),
                source="Demo",
                description=card_data["description"],
                icon=card_data["icon"],
                color_theme=card_data["color_theme"],
                sparkline_data=sparkline
            )
            cards.append(card)
        
        return cards
    
    async def get_historical_data(self, indicator_id: str, days: int = 30) -> Dict[str, Any]:
        """Obtiene datos históricos elegantes para gráficos"""
        try:
            # Por ahora generar datos demo - TODO: implementar históricos reales
            import random
            
            historical_points = []
            base_value = self._get_base_value_for_indicator(indicator_id)
            current_value = base_value
            
            for i in range(days):
                date = datetime.now() - timedelta(days=days-i)
                variation = random.uniform(-0.02, 0.02)
                current_value = current_value * (1 + variation)
                
                historical_points.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "timestamp": date.isoformat(),
                    "value": round(current_value, 2)
                })
            
            values = [p["value"] for p in historical_points]
            
            return {
                "indicator_id": indicator_id,
                "title": self._get_title_for_indicator(indicator_id),
                "data_points": historical_points,
                "statistics": {
                    "current": values[-1] if values else 0,
                    "previous": values[-2] if len(values) > 1 else values[-1] if values else 0,
                    "min_value": min(values) if values else 0,
                    "max_value": max(values) if values else 0,
                    "avg_value": sum(values) / len(values) if values else 0,
                    "change_percent": ((values[-1] - values[0]) / values[0] * 100) if len(values) > 1 and values[0] != 0 else 0,
                    "volatility": self._calculate_volatility(values),
                    "trend": "up" if values[-1] > values[0] else "down" if values[-1] < values[0] else "stable"
                },
                "chart_config": {
                    "type": "line",
                    "smooth": True,
                    "show_points": len(historical_points) <= 30,
                    "gradient": True,
                    "color_theme": self._get_color_theme_for_indicator(indicator_id),
                    "animation": "smooth"
                },
                "period": {
                    "days": days,
                    "start_date": historical_points[0]["date"] if historical_points else None,
                    "end_date": historical_points[-1]["date"] if historical_points else None
                },
                "metadata": {
                    "source": "Demo",
                    "last_updated": datetime.now().isoformat(),
                    "data_quality": "demo"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting historical data for {indicator_id}: {e}")
            return {"error": str(e), "indicator_id": indicator_id}
    
    def _get_unit_for_indicator(self, indicator_id: str) -> str:
        """Obtiene la unidad para un indicador"""
        units = {
            "usd_oficial": "ARS",
            "usd_blue": "ARS",
            "reservas_bcra": "USD M",
            "tasa_bcra": "%",
            "inflacion": "%",
            "riesgo_pais": "pb",
            "merval": "Points"
        }
        return units.get(indicator_id, "")
    
    def _get_base_value_for_indicator(self, indicator_id: str) -> float:
        """Obtiene el valor base para un indicador"""
        base_values = {
            "usd_oficial": 987.5,
            "usd_blue": 1180.0,
            "reservas_bcra": 21500.0,
            "tasa_bcra": 118.0,
            "inflacion": 4.2,
            "riesgo_pais": 1642.0,
            "merval": 1456234.0
        }
        return base_values.get(indicator_id, 100.0)
    
    def _get_title_for_indicator(self, indicator_id: str) -> str:
        """Obtiene el título para un indicador"""
        titles = {
            "usd_oficial": "USD Oficial",
            "usd_blue": "Dólar Blue",
            "reservas_bcra": "Reservas BCRA",
            "tasa_bcra": "Tasa BCRA",
            "inflacion": "Inflación",
            "riesgo_pais": "Riesgo País",
            "merval": "Merval"
        }
        return titles.get(indicator_id, indicator_id)
    
    def _get_color_theme_for_indicator(self, indicator_id: str) -> str:
        """Obtiene el theme de color para un indicador"""
        themes = {
            "usd_oficial": "blue",
            "usd_blue": "purple",
            "reservas_bcra": "blue",
            "tasa_bcra": "red",
            "inflacion": "red",
            "riesgo_pais": "yellow",
            "merval": "green"
        }
        return themes.get(indicator_id, "blue")
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calcula volatilidad de una serie de valores"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return (variance ** 0.5) / mean * 100  # CV en porcentaje

# Instancia global
enhanced_economic_service = EnhancedEconomicService()
