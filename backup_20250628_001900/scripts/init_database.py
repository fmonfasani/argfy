# -*- coding: utf-8 -*-
"""
Script para inicializar la base de datos con datos de demo
Ejecutar: python scripts/init_database.py
"""
import sys
import os
from datetime import datetime

# Agregar el directorio padre al path para importar app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models import EconomicIndicator, HistoricalData, NewsItem
from app.services.bcra_service import generate_demo_data, generate_historical_data, generate_demo_news

def init_database_with_demo_data():
    """Inicializa la base de datos con datos de demo"""
    print("Inicializando base de datos...")
    
    # Crear tablas
    init_db()
    print("Tablas creadas correctamente")
    
    # Crear sesion de base de datos
    db = SessionLocal()
    
    try:
        # Limpiar datos existentes
        print("Limpiando datos existentes...")
        db.query(EconomicIndicator).delete()
        db.query(HistoricalData).delete()
        db.query(NewsItem).delete()
        db.commit()
        
        # Generar e insertar indicadores actuales
        print("Generando indicadores economicos...")
        demo_indicators = generate_demo_data()
        
        for item in demo_indicators:
            indicator = EconomicIndicator(**item)
            db.add(indicator)
        
        db.commit()
        print(f"Indicadores creados: {len(demo_indicators)}")
        
        # Generar e insertar datos historicos
        print("Generando datos historicos...")
        key_indicators = ['dolar_blue', 'dolar_oficial', 'riesgo_pais', 'inflacion_mensual', 'reservas_bcra', 'merval']
        
        total_historical = 0
        for indicator_type in key_indicators:
            historical_data = generate_historical_data(indicator_type, days=30)
            
            for item in historical_data:
                hist_data = HistoricalData(**item)
                db.add(hist_data)
                total_historical += 1
        
        db.commit()
        print(f"Registros historicos creados: {total_historical}")
        
        # Generar e insertar noticias
        print("Generando noticias...")
        demo_news = generate_demo_news()
        
        for item in demo_news:
            news_item = NewsItem(**item)
            db.add(news_item)
        
        db.commit()
        print(f"Noticias creadas: {len(demo_news)}")
        
        print("\nBase de datos inicializada correctamente!")
        print("Puedes iniciar el servidor con: uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database_with_demo_data()
