# backend/app/models.py
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text
from .database import Base
from datetime import datetime

class EconomicIndicator(Base):
    __tablename__ = "economic_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    indicator_type = Column(String, index=True)  # "dolar_blue", "inflacion", etc.
    value = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)
    source = Column(String)  # "BCRA", "INDEC", etc.
    is_active = Column(Boolean, default=True)
    metadata_info = Column(Text, nullable=True)  # JSON adicional
    
    def __repr__(self):
        return f"<EconomicIndicator(type={self.indicator_type}, value={self.value})>"

class HistoricalData(Base):
    __tablename__ = "historical_data"
    
    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(String, index=True)
    value = Column(Float)
    date = Column(DateTime)
    period = Column(String)  # "daily", "monthly", "yearly"
    source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<HistoricalData(indicator={self.indicator_id}, value={self.value})>"

class NewsItem(Base):
    __tablename__ = "news_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500))
    summary = Column(Text)
    category = Column(String(100))
    source = Column(String(100))
    url = Column(String(500), nullable=True)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_featured = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<NewsItem(title={self.title[:50]})>"