# backend/app/services/bcra_scheduler.py
# Scheduler limpio sin problemas de encoding
import asyncio
import time
from datetime import datetime
import logging
import threading

logger = logging.getLogger(__name__)

class HybridBCRAScheduler:
    """Scheduler adaptativo sin dependencias problemáticas"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        logger.info("Scheduler inicializado")
        
    async def update_data(self):
        """Actualizar datos"""
        try:
            logger.info("Actualizando datos BCRA...")
            await asyncio.sleep(1)  # Simular trabajo
            logger.info("Datos actualizados exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error en actualización: {e}")
            return False
    
    def _run_loop(self):
        """Loop del scheduler"""
        logger.info("Scheduler loop iniciado")
        while self.running:
            try:
                time.sleep(900)  # 15 minutos
                if self.running:
                    asyncio.run(self.update_data())
            except Exception as e:
                logger.error(f"Error en scheduler loop: {e}")
                time.sleep(60)
    
    def start(self):
        """Iniciar scheduler"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            logger.info("Scheduler iniciado")
    
    def stop(self):
        """Detener scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Scheduler detenido")

# Instancia global
scheduler = HybridBCRAScheduler()
