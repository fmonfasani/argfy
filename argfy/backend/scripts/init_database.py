#!/usr/bin/env python3
# backend/scripts/init_database.py
"""
Script de inicialización de base de datos con datos demo
"""
import sys
import os
from datetime import datetime, timedelta
import logging
import asyncio

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, get_db, init_db
from app.models import EconomicIndicator, HistoricalData, Configuration, HealthCheck
from app.services.bcra_service import bcra_service
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Crear todas las tablas"""
    logger.info("🏗️ Creando tablas de base de datos...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas exitosamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {e}")
        return False

def load_demo_data():
    """Cargar datos demo iniciales"""
    logger.info("📊 Cargando datos demo...")
    
    db = next(get_db())
    try:
        # Verificar si ya existen datos
        existing_count = db.query(EconomicIndicator).count()
        if existing_count > 0:
            logger.info(f"ℹ️ Ya existen {existing_count} indicadores, saltando carga demo")
            return True

        # Datos demo actuales
        demo_indicators = [
            # Economía
            {
                "indicator_type": "usd_mayorista",
                "value": 1180.0,
                "source": "DEMO",
                "unit": "ARS",
                "label": "USD Mayorista",
                "category": "exchange"
            },
            {
                "indicator_type": "usd_minorista", 
                "value": 1190.0,
                "source": "DEMO",
                "unit": "ARS",
                "label": "USD Minorista",
                "category": "exchange"
            },
            {
                "indicator_type": "dolar_blue",
                "value": 1350.0,
                "source": "DEMO",
                "unit": "ARS",
                "label": "Dólar Blue",
                "category": "exchange"
            },
            {
                "indicator_type": "reservas_internacionales",
                "value": 41200.0,
                "source": "DEMO",
                "unit": "USD M",
                "label": "Reservas BCRA",
                "category": "monetary"
            },
            {
                "indicator_type": "tasa_politica",
                "value": 40.0,
                "source": "DEMO", 
                "unit": "%",
                "label": "Tasa Política Monetaria",
                "category": "monetary"
            },
            {
                "indicator_type": "inflacion_mensual",
                "value": 3.2,
                "source": "DEMO",
                "unit": "%",
                "label": "Inflación Mensual",
                "category": "inflation"
            },
            {
                "indicator_type": "pbi",
                "value": -1.4,
                "source": "DEMO",
                "unit": "%",
                "label": "PBI",
                "category": "growth"
            },
            {
                "indicator_type": "desempleo",
                "value": 6.2,
                "source": "DEMO",
                "unit": "%", 
                "label": "Desempleo",
                "category": "employment"
            },
            # Mercados
            {
                "indicator_type": "merval",
                "value": 1847523.0,
                "source": "DEMO",
                "unit": "puntos",
                "label": "S&P Merval",
                "category": "equity"
            },
            {
                "indicator_type": "riesgo_pais",
                "value": 1642.0,
                "source": "DEMO",
                "unit": "pb",
                "label": "Riesgo País",
                "category": "risk"
            },
            # Finanzas
            {
                "indicator_type": "plazo_fijo_30",
                "value": 118.0,
                "source": "DEMO",
                "unit": "%",
                "label": "Plazo Fijo 30 días",
                "category": "rates"
            },
            {
                "indicator_type": "tasa_tarjeta_credito",
                "value": 195.0,
                "source": "DEMO",
                "unit": "%",
                "label": "Tasa Tarjeta Crédito",
                "category": "rates"
            }
        ]

        # Insertar indicadores demo
        for demo_data in demo_indicators:
            indicator = EconomicIndicator(
                indicator_type=demo_data["indicator_type"],
                value=demo_data["value"],
                source=demo_data["source"],
                unit=demo_data["unit"],
                label=demo_data["label"],
                category=demo_data["category"],
                date=datetime.now(),
                is_active=True
            )
            db.add(indicator)

        db.commit()
        logger.info(f"✅ Cargados {len(demo_indicators)} indicadores demo")
        return True

    except Exception as e:
        logger.error(f"❌ Error cargando datos demo: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def generate_historical_data():
    """Generar datos históricos demo para gráficos"""
    logger.info("📈 Generando datos históricos demo...")
    
    db = next(get_db())
    try:
        # Verificar si ya existen datos históricos
        existing_count = db.query(HistoricalData).count()
        if existing_count > 0:
            logger.info(f"ℹ️ Ya existen {existing_count} datos históricos")
            return True

        # Indicadores para los que generar históricos
        indicators_to_generate = [
            {"type": "dolar_blue", "base_value": 1350.0, "volatility": 0.02},
            {"type": "merval", "base_value": 1847523.0, "volatility": 0.03},
            {"type": "reservas_internacionales", "base_value": 41200.0, "volatility": 0.01},
            {"type": "inflacion_mensual", "base_value": 3.2, "volatility": 0.1},
            {"type": "riesgo_pais", "base_value": 1642.0, "volatility": 0.05}
        ]

        import random
        
        for indicator in indicators_to_generate:
            current_value = indicator["base_value"]
            
            # Generar 90 días de datos
            for days_ago in range(90, 0, -1):
                # Variación aleatoria
                variation = random.uniform(-indicator["volatility"], indicator["volatility"])
                current_value = current_value * (1 + variation)
                
                date = datetime.now() - timedelta(days=days_ago)
                
                historical_point = HistoricalData(
                    indicator_type=indicator["type"],
                    value=round(current_value, 2),
                    date=date,
                    source="DEMO",
                    period="daily"
                )
                db.add(historical_point)

        db.commit()
        logger.info("✅ Datos históricos generados")
        return True

    except Exception as e:
        logger.error(f"❌ Error generando datos históricos: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def create_initial_config():
    """Crear configuración inicial del sistema"""
    logger.info("⚙️ Creando configuración inicial...")
    
    db = next(get_db())
    try:
        # Verificar si ya existe configuración
        existing_count = db.query(Configuration).count()
        if existing_count > 0:
            logger.info("ℹ️ Configuración ya existe")
            return True

        initial_configs = [
            {
                "key": "api_rate_limit",
                "value": "100",
                "value_type": "int",
                "description": "Rate limit por minuto para la API",
                "category": "api"
            },
            {
                "key": "demo_mode",
                "value": "true",
                "value_type": "bool", 
                "description": "Modo demo activado",
                "category": "system"
            },
            {
                "key": "cache_ttl_seconds",
                "value": "300",
                "value_type": "int",
                "description": "TTL del caché en segundos",
                "category": "performance"
            },
            {
                "key": "scheduler_enabled",
                "value": "true",
                "value_type": "bool",
                "description": "Scheduler automático habilitado",
                "category": "system"
            }
        ]

        for config_data in initial_configs:
            config = Configuration(
                key=config_data["key"],
                value=config_data["value"],
                value_type=config_data["value_type"],
                description=config_data["description"],
                category=config_data["category"],
                is_active=True
            )
            db.add(config)

        db.commit()
        logger.info(f"✅ Configuración inicial creada")
        return True

    except Exception as e:
        logger.error(f"❌ Error creando configuración: {e}")
        db.rollback()
        return False
    finally:
        db.close()

async def try_fetch_real_data():
    """Intentar obtener datos reales del BCRA"""
    logger.info("🌐 Intentando obtener datos reales del BCRA...")
    
    try:
        async with bcra_service as service:
            data = await service.get_current_indicators()
            
            if data.get("source") != "FALLBACK_DATA" and data.get("indicators"):
                logger.info("✅ Datos reales obtenidos del BCRA")
                
                # Guardar datos reales en la BD
                db = next(get_db())
                try:
                    for key, indicator_data in data["indicators"].items():
                        # Desactivar datos demo del mismo tipo
                        db.query(EconomicIndicator).filter(
                            EconomicIndicator.indicator_type == key,
                            EconomicIndicator.source == "DEMO"
                        ).update({"is_active": False})
                        
                        # Crear indicador con datos reales
                        real_indicator = EconomicIndicator(
                            indicator_type=key,
                            value=indicator_data["value"],
                            source=indicator_data["source"],
                            unit=indicator_data.get("unit"),
                            label=indicator_data.get("label"),
                            category=indicator_data.get("category"),
                            date=datetime.now(),
                            is_active=True
                        )
                        db.add(real_indicator)
                    
                    db.commit()
                    logger.info("✅ Datos reales guardados en BD")
                    return True
                        
                except Exception as e:
                    logger.error(f"❌ Error guardando datos reales: {e}")
                    db.rollback()
                    return False
                finally:
                    db.close()
            else:
                logger.warning("⚠️ BCRA API no disponible, usando datos demo")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error obteniendo datos reales: {e}")
        return False

def create_initial_health_check():
    """Crear health check inicial"""
    logger.info("🏥 Creando health check inicial...")
    
    db = next(get_db())
    try:
        health_check = HealthCheck(
            status="healthy",
            services='{"database": true, "api": true}',
            uptime_seconds=0.0,
            timestamp=datetime.now()
        )
        db.add(health_check)
        db.commit()
        logger.info("✅ Health check inicial creado")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creando health check: {e}")
        db.rollback()
        return False
    finally:
        db.close()

async def main():
    """Función principal de inicialización"""
    logger.info("🚀 Iniciando inicialización de base de datos...")
    
    success_steps = []
    
    # Paso 1: Crear tablas
    if create_tables():
        success_steps.append("tables")
    
    # Paso 2: Cargar datos demo
    if load_demo_data():
        success_steps.append("demo_data")
    
    # Paso 3: Generar datos históricos
    if generate_historical_data():
        success_steps.append("historical_data")
    
    # Paso 4: Crear configuración inicial
    if create_initial_config():
        success_steps.append("config")
    
    # Paso 5: Health check inicial
    if create_initial_health_check():
        success_steps.append("health_check")
    
    # Paso 6: Intentar datos reales (opcional)
    if await try_fetch_real_data():
        success_steps.append("real_data")
    
    logger.info(f"✅ Inicialización completada: {', '.join(success_steps)}")
    
    if len(success_steps) >= 4:  # Mínimo tablas + demo + históricos + config
        logger.info("🎉 Base de datos lista para usar!")
        return True
    else:
        logger.error("❌ Inicialización fallida")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Inicializar base de datos Argfy")
    parser.add_argument("--force", action="store_true", help="Forzar reinicialización")
    parser.add_argument("--real-data-only", action="store_true", help="Solo obtener datos reales")
    
    args = parser.parse_args()
    
    if args.real_data_only:
        asyncio.run(try_fetch_real_data())
    else:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)