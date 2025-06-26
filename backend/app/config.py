import os
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./data/argentina.db"
    
    # APIs Oficiales Argentina
    BCRA_API_URL: str = "https://api.bcra.gob.ar"
    INDEC_API_URL: str = "https://apis.datos.gob.ar/series/api"
    
    # APIs Financieras
    ALPHA_VANTAGE_API_KEY: str = ""
    FIXER_API_KEY: str = ""
    POLYGON_API_KEY: str = ""
    
    # Fuentes Dólar Blue
    BLUELYTICS_URL: str = "https://api.bluelytics.com.ar/v2"
    DOLAR_API_URL: str = "https://dolarapi.com/v1"
    
    # Sistema
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 300
    API_RATE_LIMIT: int = 60
    
    # Monitoring
    SENTRY_DSN: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()