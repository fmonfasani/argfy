"""
Configuración centralizada compatible con Pydantic 2
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # === EMOJIS ===
    LOG_EMOJIS: bool = True  # habilita/deshabilita iconos en los logs

    # === DATABASE ===
    DATABASE_URL: str = "sqlite:///./data/argentina.db"

    # === ENVIRONMENT ===
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # === SERVER ===
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # === SECURITY ===
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # === CORS ===
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://argfy.vercel.app",
        "https://argfy.com",
    ]

    # === EXTERNAL APIS – BCRA ===
    BCRA_BASE_URL: str = "https://api.bcra.gob.ar"
    BCRA_MONETARIAS_URL: str = (
        "https://api.bcra.gob.ar/estadisticas/v3.0/Monetarias"
    )
    BCRA_COTIZACIONES_URL: str = (
        "https://api.bcra.gob.ar/estadisticas/v1.0/Cotizaciones"
    )
    BCRA_DEUDORES_URL: str = (
        "https://api.bcra.gob.ar/padrondefinanciadores/v1.0/Deudas"
    )
    BCRA_TIMEOUT: int = 30
    BCRA_CACHE_TTL: int = 300  # 5 min

    # === Otros APIs ===
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    FIXER_API_KEY: Optional[str] = None

    # === CACHE ===
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 300

    # === SCHEDULER ===
    ENABLE_SCHEDULER: bool = True
    UPDATE_INTERVAL_MINUTES: int = 15

    # === MONITORING ===
    ENABLE_MONITORING: bool = True
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None

    # === RATE LIMITING ===
    API_RATE_LIMIT: int = 100  # rqs/min

    # === DATA SOURCES ===
    ENABLE_BCRA: bool = True
    ENABLE_FALLBACK_DATA: bool = True

    # === DEMO MODE ===
    DEMO_MODE: bool = True
    DEMO_DATA_REFRESH_MINUTES: int = 60

    # ---------- VALIDADORES ----------
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def ensure_sqlite_path(cls, v: str):
        if v.startswith("sqlite:///"):
            db_path = v.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return v

    # ---------- PROPIEDADES ----------
    @property
    def is_production(self) -> bool:  # noqa: D401
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:  # noqa: D401
        return self.ENVIRONMENT == "development"

    @property
    def log_config(self) -> dict:
        """Configuración de logging lista para dictConfig."""

        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[{levelname}] {asctime} - {name}: {message}",
                    "style": "{",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "detailed": {
                    "format": (
                        "[{levelname}] {asctime} - {name}:{lineno} - {funcName}(): {message}"
                    ),
                    "style": "{",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": self.LOG_LEVEL,
                    # encoding no es parámetro válido en StreamHandler < 3.12
                },
                "file": {
                    "class": "logging.FileHandler",
                    "filename": "logs/argfy.log",
                    "formatter": "detailed",
                    "level": self.LOG_LEVEL,
                    "encoding": "utf-8",  # aquí sí es válido
                },
            },
            "root": {
                "level": self.LOG_LEVEL,
                "handlers": ["console", "file"],
            },
            "loggers": {
                "argfy": {
                    "level": self.LOG_LEVEL,
                    "handlers": ["console", "file"],
                    "propagate": False,
                },
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }

    # ---------- CONFIG GLOBAL ----------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # usa "forbid" si prefieres rechazo estricto
    )


# ------- HELPERS -----------------------------------------------------------
@lru_cache()
def get_settings() -> Settings:
    """Instancia caché de Settings para inyección en toda la app."""
    return Settings()


settings = get_settings()

# -------- utilidades para crear .env de ejemplo ----------------------------
ENV_TEMPLATE = """\
# === ARGFY PLATFORM CONFIGURATION ===
# Copia este bloque a .env y modifica lo necesario

DATABASE_URL=sqlite:///./data/argentina.db
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000
RELOAD=true
SECRET_KEY=change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000,https://argfy.vercel.app
ALPHA_VANTAGE_API_KEY=
FIXER_API_KEY=
REDIS_URL=redis://localhost:6379
CACHE_TTL=300
ENABLE_SCHEDULER=true
UPDATE_INTERVAL_MINUTES=15
ENABLE_MONITORING=true
LOG_LEVEL=INFO
SENTRY_DSN=
API_RATE_LIMIT=100
DEMO_MODE=true
DEMO_DATA_REFRESH_MINUTES=60
"""


def create_env_file() -> None:
    """Crea .env inicial si no existe."""
    if not os.path.exists(".env"):
        with open(".env", "w", encoding="utf-8") as f:
            f.write(ENV_TEMPLATE)
        print("✅ .env creado desde la plantilla")
    else:
        print("ℹ️  .env ya existe")


if __name__ == "__main__":
    create_env_file()
    print("Settings loaded ✔")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database:    {settings.DATABASE_URL}")
    print(f"Debug:       {settings.DEBUG}")
