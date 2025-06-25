# backend/scripts/init_database.py
"""
Script para inicializar la base de datos con datos de demo
Ejecutar: python scripts/init_database.py
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Agregar el directorio padre al path para importar app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models import EconomicIndicator, HistoricalData, NewsItem
from app.services.bcra_service import generate_demo_data, generate_historical_data, generate_demo_news

def init_database_with_demo_data():
    """Inicializa la base de datos con datos de demo"""
    print("🚀 Inicializando base de datos...")
    
    # Crear tablas
    init_db()
    print("✅ Tablas creadas")
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Limpiar datos existentes
        print("🧹 Limpiando datos existentes...")
        db.query(EconomicIndicator).delete()
        db.query(HistoricalData).delete()
        db.query(NewsItem).delete()
        db.commit()
        
        # Generar e insertar indicadores actuales
        print("📊 Generando indicadores económicos...")
        demo_indicators = generate_demo_data()
        
        for item in demo_indicators:
            indicator = EconomicIndicator(**item)
            db.add(indicator)
        
        db.commit()
        print(f"✅ {len(demo_indicators)} indicadores creados")
        
        # Generar e insertar datos históricos
        print("📈 Generando datos históricos...")
        key_indicators = ['dolar_blue', 'dolar_oficial', 'riesgo_pais', 'inflacion_mensual', 'reservas_bcra', 'merval']
        
        total_historical = 0
        for indicator_type in key_indicators:
            historical_data = generate_historical_data(indicator_type, days=30)
            
            for item in historical_data:
                hist_data = HistoricalData(**item)
                db.add(hist_data)
                total_historical += 1
        
        db.commit()
        print(f"✅ {total_historical} registros históricos creados")
        
        # Generar e insertar noticias
        print("📰 Generando noticias...")
        demo_news = generate_demo_news()
        
        for item in demo_news:
            news_item = NewsItem(**item)
            db.add(news_item)
        
        db.commit()
        print(f"✅ {len(demo_news)} noticias creadas")
        
        # Verificar datos creados
        print("\n📋 Resumen de datos creados:")
        print(f"   • Indicadores económicos: {db.query(EconomicIndicator).count()}")
        print(f"   • Registros históricos: {db.query(HistoricalData).count()}")
        print(f"   • Noticias: {db.query(NewsItem).count()}")
        
        print("\n🎉 Base de datos inicializada correctamente!")
        print("   Puedes iniciar el servidor con: uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def add_more_historical_data():
    """Agrega más datos históricos (opcional)"""
    print("📈 Agregando más datos históricos...")
    
    db = SessionLocal()
    
    try:
        # Generar datos históricos para más días
        key_indicators = ['dolar_blue', 'riesgo_pais', 'merval']
        
        for indicator_type in key_indicators:
            # Datos de 90 días
            historical_data = generate_historical_data(indicator_type, days=90)
            
            # Solo agregar los datos más antiguos (días 30-90)
            older_data = historical_data[:60]  # Primeros 60 días (más antiguos)
            
            for item in older_data:
                # Verificar si ya existe
                existing = db.query(HistoricalData).filter(
                    HistoricalData.indicator_id == item['indicator_id'],
                    HistoricalData.date == item['date']
                ).first()
                
                if not existing:
                    hist_data = HistoricalData(**item)
                    db.add(hist_data)
        
        db.commit()
        print("✅ Datos históricos adicionales agregados")
        
    except Exception as e:
        print(f"❌ Error al agregar datos históricos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Inicializar base de datos de Argfy')
    parser.add_argument('--extend', action='store_true', help='Agregar más datos históricos')
    
    args = parser.parse_args()
    
    if args.extend:
        add_more_historical_data()
    else:
        init_database_with_demo_data()
        
        # Preguntar si agregar más datos
        response = input("\n¿Deseas agregar más datos históricos? (y/N): ")
        if response.lower() in ['y', 'yes', 'sí', 'si']:
            add_more_historical_data()