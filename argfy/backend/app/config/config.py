# app/config.py - Archivo de configuración principal
"""
Configuración centralizada para Argfy Platform
Compatible con Python 3.11+ y dependencias mínimas
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración principal de la aplicación"""
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./data/argentina.db",
        description="URL de conexión a la base de datos"
    )
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="Entorno de ejecución")
    DEBUG: bool = Field(default=True, description="Modo debug")
    
    # Security
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-please",
        description="Clave secreta para JWT y encryption"
    )
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://argfy.com",
            "https://www.argfy.com"
        ],
        description="Orígenes permitidos para CORS"
    )
    
    # API Configuration
    API_PREFIX: str = Field(default="/api/v1", description="Prefijo de la API")
    API_VERSION: str = Field(default="1.0.0", description="Versión de la API")
    
    # External APIs
    BCRA_API_URL: str = Field(
        default="https://api.bcra.gob.ar",
        description="URL base de la API del BCRA"
    )
    
    # Cache Settings
    CACHE_TTL: int = Field(default=300, description="TTL del cache en segundos")
    
    # Auth / JWT
    JWT_SECRET: str = Field(
        default="dev-jwt-secret-change-in-production",
        description="Secreto para firmar JWT"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="Algoritmo JWT")
    JWT_EXPIRY_HOURS: int = Field(default=72, description="Expiración JWT en horas")
    GOOGLE_CLIENT_ID: str = Field(default="", description="Google OAuth client ID")
    GOOGLE_CLIENT_SECRET: str = Field(default="", description="Google OAuth client secret")

    # Mercado Pago
    MP_ACCESS_TOKEN: str = Field(default="", description="Mercado Pago access token")
    MP_WEBHOOK_SECRET: str = Field(default="", description="Mercado Pago webhook secret")
    MP_SUCCESS_URL: str = Field(default="http://localhost:3000/account/billing", description="URL post-checkout exitoso")
    MP_FAILURE_URL: str = Field(default="http://localhost:3000/pricing", description="URL post-checkout fallido")
    MP_PENDING_URL: str = Field(default="http://localhost:3000/account/billing", description="URL post-checkout pendiente")

    PLAN_PRICES: dict = Field(
        default={
            "pro": {"price": 999, "title": "Argfy Pro", "description": "Screener ilimitado + API access"},
            "enterprise": {"price": 4999, "title": "Argfy Enterprise", "description": "Todo Pro + soporte prioritario"},
        },
        description="Precios de planes en ARS (centavos)"
    )

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Límite de requests por minuto")
    
    # Monitoring
    ENABLE_MONITORING: bool = Field(default=True, description="Habilitar monitoreo")
    
    # Data Refresh
    DATA_REFRESH_INTERVAL: int = Field(
        default=900,
        description="Intervalo de actualización de datos en segundos (15 min)"
    )
    UPDATE_INTERVAL_MINUTES: int = Field(
        default=15,
        description="Intervalo del legacy UnifiedScheduler en minutos"
    )
    ENABLE_SCHEDULER: bool = Field(default=True, description="Habilitar APScheduler/UnifiedScheduler")
    DEMO_MODE: bool = Field(default=False, description="Modo demo: usa datos sintéticos en vez de APIs reales")
    LOG_EMOJIS: bool = Field(default=False, description="Permitir emojis en logs (off en prod para compat con stdout ASCII)")
    REDIS_URL: str = Field(default="", description="URL de Redis; vacío deshabilita el cache")
    SENTRY_DSN: str = Field(default="", description="DSN de Sentry; vacío deshabilita reporting")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Nivel de logging")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
        # Ejemplos de variables de entorno
        schema_extra = {
            "example": {
                "DATABASE_URL": "postgresql://user:pass@localhost/argfy",
                "ENVIRONMENT": "production", 
                "DEBUG": False,
                "SECRET_KEY": "super-secret-key-for-production",
                "CORS_ORIGINS": ["https://argfy.com"],
                "BCRA_API_URL": "https://api.bcra.gob.ar"
            }
        }

# Instancia global de configuración
settings = Settings()

# Configuraciones derivadas
class DatabaseConfig:
    """Configuración específica de base de datos"""
    
    @staticmethod
    def get_database_url() -> str:
        """Obtener URL de base de datos con validaciones"""
        url = settings.DATABASE_URL
        
        # Crear directorio data si es SQLite
        if url.startswith("sqlite"):
            os.makedirs("data", exist_ok=True)
            
        return url
    
    @staticmethod
    def is_sqlite() -> bool:
        """Verificar si estamos usando SQLite"""
        return settings.DATABASE_URL.startswith("sqlite")
    
    @staticmethod
    def is_postgresql() -> bool:
        """Verificar si estamos usando PostgreSQL"""
        return settings.DATABASE_URL.startswith("postgresql")

class APIConfig:
    """Configuración específica de la API"""
    
    @staticmethod
    def get_full_cors_origins() -> List[str]:
        """Obtener lista completa de orígenes CORS"""
        origins = settings.CORS_ORIGINS.copy()
        
        # Agregar localhost variants si estamos en desarrollo
        if settings.DEBUG:
            localhost_variants = [
                "http://localhost:3000",
                "http://127.0.0.1:3000", 
                "http://localhost:3001",
                "http://127.0.0.1:3001"
            ]
            for variant in localhost_variants:
                if variant not in origins:
                    origins.append(variant)
                    
        return origins

# Funciones de utilidad
def get_environment() -> str:
    """Obtener entorno actual"""
    return settings.ENVIRONMENT

def is_development() -> bool:
    """Verificar si estamos en desarrollo"""
    return settings.ENVIRONMENT == "development"

def is_production() -> bool:
    """Verificar si estamos en producción"""
    return settings.ENVIRONMENT == "production"

def get_database_url() -> str:
    """Obtener URL de base de datos"""
    return DatabaseConfig.get_database_url()

# Export para compatibilidad
__all__ = [
    "settings",
    "Settings", 
    "DatabaseConfig",
    "APIConfig",
    "get_environment",
    "is_development", 
    "is_production",
    "get_database_url"
]