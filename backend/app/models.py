# backend/app/models.py
"""
Modelos de base de datos consolidados y limpios
Incluye todas las tablas necesarias sin duplicaciones
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text, Index
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base

class EconomicIndicator(Base):
    """
    Modelo principal para indicadores económicos
    Consolidado y optimizado para el demo
    """
    __tablename__ = "economic_indicators"

    id = Column(Integer, primary_key=True, index=True)
    indicator_type = Column(String(50), index=True, nullable=False)  # "usd_mayorista", "inflacion_mensual", etc.
    value = Column(Float, nullable=False)
    source = Column(String(20), nullable=False)  # "BCRA", "INDEC", "DEMO", etc.
    date = Column(DateTime, default=func.now(), index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Metadatos adicionales
    unit = Column(String(10))  # "ARS", "%", "USD M", etc.
    label = Column(String(100))  # Label human-readable
    category = Column(String(30))  # "exchange", "monetary", "inflation", etc.
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Índices compuestos para optimización
    __table_args__ = (
        Index('idx_indicator_type_date', 'indicator_type', 'date'),
        Index('idx_indicator_active_type', 'is_active', 'indicator_type'),
        Index('idx_indicator_source_date', 'source', 'date'),
    )

    def __repr__(self):
        return f"<EconomicIndicator(type={self.indicator_type}, value={self.value}, source={self.source})>"

class HistoricalData(Base):
    """
    Datos históricos para gráficos y análisis
    Separado de EconomicIndicator para optimización
    """
    __tablename__ = "historical_data"

    id = Column(Integer, primary_key=True, index=True)
    indicator_type = Column(String(50), index=True, nullable=False)
    value = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    source = Column(String(20), nullable=False)
    
    # Período de agregación
    period = Column(String(10), default="daily")  # "daily", "weekly", "monthly", "yearly"
    
    # Para estadísticas
    high = Column(Float)  # Valor máximo del período
    low = Column(Float)   # Valor mínimo del período
    open = Column(Float)  # Valor de apertura
    close = Column(Float) # Valor de cierre
    volume = Column(Float) # Volumen si aplica
    
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index('idx_historical_type_date', 'indicator_type', 'date'),
        Index('idx_historical_period_date', 'period', 'date'),
    )

    def __repr__(self):
        return f"<HistoricalData(type={self.indicator_type}, value={self.value}, date={self.date})>"

class NewsItem(Base):
    """
    Noticias económicas relacionadas
    Para futuras funcionalidades
    """
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    source = Column(String(50), nullable=False)
    url = Column(String(500))
    author = Column(String(100))
    
    # Categorización
    category = Column(String(30))  # "economy", "markets", "government", etc.
    tags = Column(String(200))     # Tags separados por comas
    
    # Metadata
    published_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    
    # Análisis de sentimiento (futuro)
    sentiment_score = Column(Float)  # -1 a 1
    relevance_score = Column(Float)  # 0 a 1
    
    is_active = Column(Boolean, default=True, index=True)

    __table_args__ = (
        Index('idx_news_category_published', 'category', 'published_at'),
        Index('idx_news_source_published', 'source', 'published_at'),
    )

    def __repr__(self):
        return f"<NewsItem(title={self.title[:50]}, source={self.source})>"

class HealthCheck(Base):
    """
    Health checks del sistema
    Para monitoreo y debugging
    """
    __tablename__ = "health_checks"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(20), nullable=False)  # "healthy", "degraded", "unhealthy"
    services = Column(Text)  # JSON string con estado de servicios
    uptime_seconds = Column(Float)
    
    # Métricas del sistema
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_percent = Column(Float)
    
    # Contadores
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    
    timestamp = Column(DateTime, default=func.now(), index=True)

    def __repr__(self):
        return f"<HealthCheck(status={self.status}, timestamp={self.timestamp})>"

class APIUsage(Base):
    """
    Tracking de uso de API
    Para analytics y rate limiting futuro
    """
    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(100), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    
    # Client info
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(String(500))
    
    # Timing
    response_time_ms = Column(Float)
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Para rate limiting
    client_id = Column(String(100))  # API key o session ID
    
    __table_args__ = (
        Index('idx_api_usage_endpoint_timestamp', 'endpoint', 'timestamp'),
        Index('idx_api_usage_client_timestamp', 'client_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<APIUsage(endpoint={self.endpoint}, status={self.status_code})>"

class Configuration(Base):
    """
    Configuración dinámica de la aplicación
    Para settings que pueden cambiar sin redeploy
    """
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    value_type = Column(String(20), default="string")  # "string", "int", "float", "bool", "json"
    
    description = Column(String(200))
    category = Column(String(50))  # "api", "scheduler", "monitoring", etc.
    
    # Control de cambios
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_by = Column(String(50))  # Usuario que hizo el cambio

    def __repr__(self):
        return f"<Configuration(key={self.key}, value={self.value[:50]})>"

    def get_typed_value(self):
        """Retorna el valor convertido al tipo correcto"""
        if self.value_type == "int":
            return int(self.value)
        elif self.value_type == "float":
            return float(self.value)
        elif self.value_type == "bool":
            return self.value.lower() in ("true", "1", "yes", "on")
        elif self.value_type == "json":
            import json
            return json.loads(self.value)
        else:
            return self.value

# === UTILITY FUNCTIONS ===

def get_latest_indicator(db, indicator_type: str) -> EconomicIndicator:
    """Obtiene el último valor de un indicador"""
    return db.query(EconomicIndicator).filter(
        EconomicIndicator.indicator_type == indicator_type,
        EconomicIndicator.is_active == True
    ).order_by(EconomicIndicator.date.desc()).first()

def get_indicator_history(db, indicator_type: str, days: int = 30) -> list:
    """Obtiene el historial de un indicador"""
    cutoff_date = datetime.now() - timedelta(days=days)
    return db.query(HistoricalData).filter(
        HistoricalData.indicator_type == indicator_type,
        HistoricalData.date >= cutoff_date
    ).order_by(HistoricalData.date.asc()).all()

def get_system_health(db) -> HealthCheck:
    """Obtiene el último health check"""
    return db.query(HealthCheck).order_by(
        HealthCheck.timestamp.desc()
    ).first()

def cleanup_old_data(db, days_to_keep: int = 90):
    """Limpia datos viejos"""
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    # Limpiar indicadores inactivos viejos
    db.query(EconomicIndicator).filter(
        EconomicIndicator.date < cutoff_date,
        EconomicIndicator.is_active == False
    ).delete()
    
    # Limpiar health checks viejos
    db.query(HealthCheck).filter(
        HealthCheck.timestamp < cutoff_date
    ).delete()
    
    # Limpiar API usage viejo
    db.query(APIUsage).filter(
        APIUsage.timestamp < cutoff_date
    ).delete()
    
    db.commit()
    return True