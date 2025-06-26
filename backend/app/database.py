from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

# Base de datos SQLite para desarrollo
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/argentina.db")

# Crear directorio si no existe
os.makedirs("data", exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    },
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=False  # No logs SQL en producción
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializar base de datos y crear tablas"""
    Base.metadata.create_all(bind=engine)
