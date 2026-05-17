# backend/app/models.py
"""
Modelos de base de datos consolidados y limpios
Incluye todas las tablas necesarias sin duplicaciones
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, BigInteger, Boolean, Text, Index, ForeignKey, SmallInteger, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from .database import Base, IS_SQLITE

# JSONB en Postgres, JSON en SQLite (transparente)
JsonType = JSON if IS_SQLITE else JSONB

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

# === FUNDAMENTALS / CEDEARs (migrado desde valuarty) ===

class Company(Base):
    """
    Master único de empresas. Una fila por byma_ticker.
    Alineado con universe/companies.csv del entregable Fase 2.
    """
    __tablename__ = "companies"

    byma_ticker  = Column(String(20), primary_key=True)
    ticker_sec   = Column(String(20), index=True)
    cik          = Column(String(20), index=True)
    isin         = Column(String(20))
    nombre       = Column(String(200))
    exchange     = Column(String(20))
    country      = Column(String(8))
    sector       = Column(String(80))
    industry     = Column(String(120))
    currency     = Column(String(8))
    source_tier  = Column(SmallInteger)
    has_sec      = Column(Boolean, default=False)
    has_yf       = Column(Boolean, default=False)
    has_fmp      = Column(Boolean, default=False)
    created_at   = Column(DateTime, default=func.now())
    updated_at   = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Company(byma={self.byma_ticker}, sec={self.ticker_sec})>"


class PriceDaily(Base):
    """Daily OHLCV. PK compuesta (byma_ticker, date)."""
    __tablename__ = "prices_daily"

    byma_ticker = Column(String(20), ForeignKey("companies.byma_ticker", ondelete="CASCADE"), primary_key=True)
    date        = Column(Date, primary_key=True)
    open        = Column(Float)
    high        = Column(Float)
    low         = Column(Float)
    close       = Column(Float)
    adj_close   = Column(Float)
    volume      = Column(BigInteger)
    currency    = Column(String(8))
    source      = Column(String(20))

    __table_args__ = (
        Index("idx_prices_date", "date"),
    )


class FundamentalRaw(Base):
    """Bag JSONB con métricas crudas XBRL/yfinance/FMP. 1 fila por CIK
    (varios byma_tickers comparten CIK; el join se hace via companies.cik)."""
    __tablename__ = "fundamentals_raw"

    cik         = Column(String(20), primary_key=True)
    ticker_sec  = Column(String(20), index=True)
    source      = Column(String(20))
    as_of       = Column(DateTime)
    currency    = Column(String(8))
    metrics     = Column(JsonType, nullable=False)
    updated_at  = Column(DateTime, default=func.now(), onupdate=func.now())


class FundamentalQuarterly(Base):
    """Balances trimestrales normalizados. PK (byma_ticker, period_end)."""
    __tablename__ = "fundamentals_quarterly"

    byma_ticker     = Column(String(20), ForeignKey("companies.byma_ticker", ondelete="CASCADE"), primary_key=True)
    period_end      = Column(Date, primary_key=True)
    period_start    = Column(Date)
    fy              = Column(SmallInteger)
    fp              = Column(String(4))
    form            = Column(String(10))
    filed           = Column(Date)
    revenue         = Column(Float)
    gross_profit    = Column(Float)
    ebit            = Column(Float)
    ebitda          = Column(Float)
    net_income      = Column(Float)
    eps_diluted     = Column(Float)
    diluted_shares  = Column(Float)
    cfo             = Column(Float)
    capex           = Column(Float)
    fcf             = Column(Float)
    dividends_paid  = Column(Float)
    lt_debt         = Column(Float)
    st_debt         = Column(Float)
    total_debt      = Column(Float)
    equity          = Column(Float)
    total_assets    = Column(Float)
    cash            = Column(Float)
    currency        = Column(String(8))
    source          = Column(String(20))

    __table_args__ = (
        Index("idx_fundq_period", "period_end"),
    )


class RatioQuarterly(Base):
    """
    Ratios calculados por trimestre. Una fila por (byma_ticker, period_end).
    Reemplaza al legacy RatioSnapshot: la "última fila" se obtiene con
    MAX(period_end) por ticker.
    """
    __tablename__ = "ratios_quarterly"

    byma_ticker              = Column(String(20), ForeignKey("companies.byma_ticker", ondelete="CASCADE"), primary_key=True)
    period_end               = Column(Date, primary_key=True)
    as_of                    = Column(DateTime, default=func.now())
    ticker_sec               = Column(String(20))
    cik                      = Column(String(20))

    precio_usd               = Column(Float)
    currency                 = Column(String(8))
    exchange                 = Column(String(20))
    year_high                = Column(Float)
    year_low                 = Column(Float)
    dif_max_52w              = Column(Float)
    dif_min_52w              = Column(Float)

    per_ttm                  = Column(Float)
    eps_ttm_diluted          = Column(Float)
    margen_neto_ttm          = Column(Float)
    roe_cagr_5y              = Column(Float)
    deuda_lp_sobre_ebitda    = Column(Float)
    deuda_total_sobre_ebitda = Column(Float)
    fcfonce_equity_lp        = Column(Float)
    fcfonce_neto_caja        = Column(Float)
    payout_ttm               = Column(Float)
    cagr_eps_5y              = Column(Float)

    revenue_ttm              = Column(Float)
    netincome_ttm            = Column(Float)
    ebitda_ttm               = Column(Float)
    fcf_ttm                  = Column(Float)
    diluted_shares           = Column(Float)
    equity                   = Column(Float)
    lt_debt                  = Column(Float)
    deuda_total              = Column(Float)

    __table_args__ = (
        Index("idx_ratios_per",        "per_ttm"),
        Index("idx_ratios_roe",        "roe_cagr_5y"),
        Index("idx_ratios_period_end", "period_end"),
    )

    def __repr__(self):
        return f"<RatioQuarterly(byma={self.byma_ticker}, period={self.period_end}, per={self.per_ttm})>"


class ETLRun(Base):
    """Registro de ejecución de jobs ETL con protección anti-duplicados."""
    __tablename__ = "etl_runs"

    id              = Column(String(36), primary_key=True)  # UUID
    job_name        = Column(String(50), nullable=False)
    trigger         = Column(String(20), nullable=False)  # scheduled | manual | startup
    status          = Column(String(20), nullable=False)  # running | success | failed | partial
    started_at      = Column(DateTime, nullable=False)
    finished_at     = Column(DateTime)
    scheduled_for   = Column(Date, nullable=False)
    duration_ms     = Column(Integer)
    rows_inserted   = Column(Integer, default=0)
    rows_updated    = Column(Integer, default=0)
    errors_count    = Column(Integer, default=0)
    warnings_count  = Column(Integer, default=0)
    log_excerpt     = Column(Text)
    error_details   = Column(JsonType)
    run_metadata    = Column("metadata", JsonType)
    created_at      = Column(DateTime, default=func.now())

    __table_args__ = (
        Index("idx_etl_job_name", "job_name"),
        Index("idx_etl_started_at", "started_at"),
        UniqueConstraint("job_name", "scheduled_for", name="uq_etl_job_day"),
    )


class FxRate(Base):
    """USD/ARS daily (CCL, MEP, oficial)."""
    __tablename__ = "fx_rates"

    date    = Column(Date, primary_key=True)
    ccl     = Column(Float)
    mep     = Column(Float)
    oficial = Column(Float)
    source  = Column(String(20))


# === AUTH MODELS (Fase 0 — Multi-Tenant) ===

class Tenant(Base):
    __tablename__ = "tenants"

    id         = Column(String(36), primary_key=True)
    name       = Column(String(200), nullable=False)
    slug       = Column(String(100), unique=True, nullable=False)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())


class Subscription(Base):
    __tablename__ = "subscriptions"

    id                     = Column(String(36), primary_key=True)
    tenant_id              = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    plan                   = Column(String(20), nullable=False, default="free")
    status                 = Column(String(20), nullable=False, default="active")
    current_period_start   = Column(DateTime)
    current_period_end     = Column(DateTime)
    cancel_at_period_end   = Column(Boolean, default=False)
    mp_subscription_id     = Column(String(100))
    stripe_subscription_id = Column(String(100))
    created_at             = Column(DateTime, default=func.now())


class User(Base):
    __tablename__ = "users"

    id            = Column(String(36), primary_key=True)
    tenant_id     = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    email         = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255))
    google_id     = Column(String(100), unique=True)
    nombre        = Column(String(200))
    role          = Column(String(20), nullable=False, default="member")
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, default=func.now())


class Invitation(Base):
    __tablename__ = "invitations"

    id          = Column(String(36), primary_key=True)
    tenant_id   = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    email       = Column(String(255), nullable=False)
    role        = Column(String(20), default="member")
    token       = Column(String(64), unique=True, nullable=False, index=True)
    expires_at  = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime)
    created_at  = Column(DateTime, default=func.now())


class ApiKey(Base):
    __tablename__ = "api_keys"

    id         = Column(String(36), primary_key=True)
    tenant_id  = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    key_hash   = Column(String(64), unique=True, nullable=False, index=True)
    key_prefix = Column(String(12))
    name       = Column(String(100))
    last_used  = Column(DateTime)
    created_at = Column(DateTime, default=func.now())


class PlanFeature(Base):
    __tablename__ = "plan_features"

    plan        = Column(String(20), primary_key=True)
    feature_key = Column(String(50), primary_key=True)
    enabled     = Column(Boolean, default=False)


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