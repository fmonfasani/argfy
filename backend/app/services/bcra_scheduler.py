# backend/app/services/bcra_scheduler.py
import asyncio
import schedule
import time
from datetime import datetime
import logging
from app.services.bcra_real_data_service import BCRARealDataService

logger = logging.getLogger(__name__)

class BCRAScheduler:
    """Programador para actualizar datos del BCRA automáticamente"""
    
    def __init__(self):
        self.service = None
        self.running = False
        
    async def update_data(self):
        """Actualizar datos del BCRA"""
        try:
            async with BCRARealDataService() as service:
                logger.info("🔄 Iniciando actualización de datos BCRA...")
                
                # Obtener datos del dashboard
                dashboard_data = await service.get_dashboard_data()
                
                if dashboard_data.get("status") == "success":
                    # Guardar en base de datos
                    saved = await service.save_to_database(dashboard_data)
                    
                    if saved:
                        logger.info("✅ Datos BCRA actualizados exitosamente")
                    else:
                        logger.error("❌ Error guardando datos en BD")
                else:
                    logger.error(f"❌ Error obteniendo datos: {dashboard_data}")
                    
        except Exception as e:
            logger.error(f"Error en actualización automática: {e}")
    
    def schedule_updates(self):
        """Programar actualizaciones automáticas"""
        # Actualizar cada 15 minutos durante horarios bancarios
        schedule.every(15).minutes.do(lambda: asyncio.run(self.update_data()))
        
        # Actualización diaria a las 9:00 AM
        schedule.every().day.at("09:00").do(lambda: asyncio.run(self.update_data()))
        
        logger.info("📅 Actualizaciones programadas: cada 15 min + diario 9:00 AM")
    
    def start(self):
        """Iniciar el programador"""
        self.running = True
        self.schedule_updates()
        
        logger.info("🚀 BCRA Scheduler iniciado")
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Revisar cada minuto
    
    def stop(self):
        """Detener el programador"""
        self.running = False
        logger.info("⏹️ BCRA Scheduler detenido")

# Inicializar en main.py
scheduler = BCRAScheduler()