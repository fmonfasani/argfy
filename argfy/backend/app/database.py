from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

# DATABASE_URL acepta:
#   sqlite:///./data/argentina.db              (default dev legacy)
#   postgresql+psycopg2://argfy:argfy_dev@localhost:5544/argfy
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/argentina.db")

IS_SQLITE = DATABASE_URL.startswith("sqlite")

if IS_SQLITE:
    os.makedirs("data", exist_ok=True)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False, "timeout": 30},
        poolclass=StaticPool,
        pool_pre_ping=True,
        echo=False,
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=1800,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
