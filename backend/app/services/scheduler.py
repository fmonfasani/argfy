# backend/app/services/scheduler.py
"""
Scheduler y Monitor Unificado
Reemplaza: bcra_scheduler.py, monitor.py, monitor_render.py, monitoring.py
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import signal
import sys

from ..config import settings
from ..database import get_db
from ..models import EconomicIndicator, HealthCheck
from .bcra_service import bcra_service

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ScheduledTask:
    """Representa una tarea programada"""
    name: str
    func: Callable
    interval_minutes: int
    next_run: datetime
    last_run: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    error_count: int = 0
    max_errors: int = 3
    enabled: bool = True
    
    def __post_init__(self):
        if self.next_run is None:
            self.next_run = datetime.now() + timedelta(minutes=self.interval_minutes)

@dataclass 
class SystemHealth:
    """Estado de salud del sistema"""
    status: str = "healthy"
    services: Dict[str, bool] = field(default_factory=dict)
    last_check: datetime = field(default_factory=datetime.now)
    uptime_seconds: float = 0
    error_count: int = 0
    warning_count: int = 0

class UnifiedScheduler:
    """
    Scheduler y monitor unificado que maneja todas las tareas programadas
    y el monitoreo de salud del sistema
    """
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.start_time = datetime.now()
        self.health = SystemHealth()
        self._setup_signal_handlers()
        self._register_default_tasks()
    
    def _setup_signal_handlers(self):
        """Configurar manejo de señales para shutdown graceful"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Manejador de señales para shutdown"""
        logger.info(f"Received signal {signum}, shutting down scheduler...")
        self.stop()
    
    def _register_default_tasks(self):
        """Registra las tareas por defecto del sistema"""
        
        # Tarea principal: actualizar datos BCRA
        self.register_task(
            name="update_bcra_data",
            func=self._update_bcra_data,
            interval_minutes=settings.UPDATE_INTERVAL_MINUTES
        )
        
        # Tarea de salud: verificar APIs
        self.register_task(
            name="health_check",
            func=self._perform_health_check,
            interval_minutes=5
        )
        
        # Tarea de limpieza: limpiar datos viejos
        self.register_task(
            name="cleanup_old_data", 
            func=self._cleanup_old_data,
            interval_minutes=60
        )
        
        # Solo en producción: monitoreo extendido
        if settings.is_production:
            self.register_task(
                name="system_metrics",
                func=self._collect_system_metrics,
                interval_minutes=10
            )
    
    def register_task(self, name: str, func: Callable, interval_minutes: int, 
                     enabled: bool = True) -> None:
        """Registra una nueva tarea programada"""
        task = ScheduledTask(
            name=name,
            func=func,
            interval_minutes=interval_minutes,
            next_run=datetime.now() + timedelta(minutes=interval_minutes),
            enabled=enabled
        )
        self.tasks[name] = task
        logger.info(f"Registered task '{name}' with {interval_minutes}min interval")
    
    def unregister_task(self, name: str) -> bool:
        """Desregistra una tarea"""
        if name in self.tasks:
            del self.tasks[name]
            logger.info(f"Unregistered task '{name}'")
            return True
        return False
    
    def enable_task(self, name: str) -> bool:
        """Habilita una tarea"""
        if name in self.tasks:
            self.tasks[name].enabled = True
            return True
        return False
    
    def disable_task(self, name: str) -> bool:
        """Deshabilita una tarea"""
        if name in self.tasks:
            self.tasks[name].enabled = False
            return True
        return False
    
    async def start(self):
        """Inicia el scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.start_time = datetime.now()
        logger.info("🚀 Unified Scheduler started")
        
        try:
            while self.running:
                await self._run_cycle()
                await asyncio.sleep(30)  # Check every 30 seconds
        except Exception as e:
            logger.error(f"Scheduler crashed: {e}")
        finally:
            logger.info("⏹️ Scheduler stopped")
    
    def stop(self):
        """Detiene el scheduler"""
        self.running = False
        
        # Cancelar tareas en ejecución
        for task in self.tasks.values():
            if task.status == TaskStatus.RUNNING:
                task.status = TaskStatus.CANCELLED
    
    async def _run_cycle(self):
        """Ejecuta un ciclo del scheduler"""
        now = datetime.now()
        
        for task_name, task in self.tasks.items():
            if not task.enabled:
                continue
                
            if task.status == TaskStatus.RUNNING:
                continue
                
            if now >= task.next_run:
                asyncio.create_task(self._execute_task(task))
    
    async def _execute_task(self, task: ScheduledTask):
        """Ejecuta una tarea específica"""
        task.status = TaskStatus.RUNNING
        task.last_run = datetime.now()
        
        try:
            logger.debug(f"Executing task: {task.name}")
            
            if asyncio.iscoroutinefunction(task.func):
                await task.func()
            else:
                task.func()
            
            task.status = TaskStatus.COMPLETED
            task.error_count = 0  # Reset error count on success
            task.next_run = datetime.now() + timedelta(minutes=task.interval_minutes)
            
            logger.debug(f"Task '{task.name}' completed successfully")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_count += 1
            
            logger.error(f"Task '{task.name}' failed: {e}")
            
            # Deshabilitar tarea si tiene demasiados errores
            if task.error_count >= task.max_errors:
                task.enabled = False
                logger.error(f"Task '{task.name}' disabled after {task.max_errors} errors")
            else:
                # Retry con backoff exponencial
                delay = min(task.interval_minutes * (2 ** task.error_count), 60)
                task.next_run = datetime.now() + timedelta(minutes=delay)
    
    async def _update_bcra_data(self):
        """Tarea principal: actualizar datos del BCRA"""
        try:
            async with bcra_service as service:
                data = await service.get_current_indicators()
                
                if data.get("source") != "FALLBACK_DATA":
                    await self._save_indicators_to_db(data["indicators"])
                    logger.info("✅ BCRA data updated successfully")
                else:
                    logger.warning("⚠️ Using fallback data, BCRA API unavailable")
                    
        except Exception as e:
            logger.error(f"Failed to update BCRA data: {e}")
            raise
    
    async def _perform_health_check(self):
        """Verifica la salud del sistema"""
        try:
            self.health.last_check = datetime.now()
            self.health.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            self.health.services = {}
            
            # Check BCRA API
            try:
                async with bcra_service as service:
                    test_data = await service.get_current_indicators()
                    self.health.services["bcra_api"] = test_data.get("source") != "FALLBACK_DATA"
            except:
                self.health.services["bcra_api"] = False
            
            # Check database
            try:
                db = next(get_db())
                db.execute("SELECT 1")
                self.health.services["database"] = True
                db.close()
            except:
                self.health.services["database"] = False
            
            # Determinar estado general
            failed_services = [k for k, v in self.health.services.items() if not v]
            if failed_services:
                self.health.status = "degraded" if len(failed_services) == 1 else "unhealthy"
                self.health.warning_count += 1 if len(failed_services) == 1 else 0
                self.health.error_count += 1 if len(failed_services) > 1 else 0
            else:
                self.health.status = "healthy"
            
            # Guardar health check en DB
            await self._save_health_check()
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.health.status = "unhealthy"
            raise
    
    async def _cleanup_old_data(self):
        """Limpia datos viejos de la base de datos"""
        try:
            cutoff_date = datetime.now() - timedelta(days=90)  # Mantener 90 días
            
            db = next(get_db())
            
            # Limpiar indicadores viejos
            deleted = db.query(EconomicIndicator).filter(
                EconomicIndicator.date < cutoff_date,
                EconomicIndicator.is_active == False
            ).delete()
            
            # Limpiar health checks viejos
            db.query(HealthCheck).filter(
                HealthCheck.timestamp < cutoff_date
            ).delete()
            
            db.commit()
            db.close()
            
            if deleted > 0:
                logger.info(f"Cleaned up {deleted} old records")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            raise
    
    async def _collect_system_metrics(self):
        """Recolecta métricas del sistema (solo en producción)"""
        try:
            import psutil
            
            # CPU y memoria
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            logger.info(f"System metrics - CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%")
            
            # Alertas si los recursos están altos
            if cpu_percent > 80:
                logger.warning(f"High CPU usage: {cpu_percent}%")
            if memory.percent > 80:
                logger.warning(f"High memory usage: {memory.percent}%")
            if disk.percent > 90:
                logger.warning(f"High disk usage: {disk.percent}%")
                
        except ImportError:
            logger.debug("psutil not available, skipping system metrics")
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    async def _save_indicators_to_db(self, indicators: Dict):
        """Guarda indicadores en la base de datos"""
        try:
            db = next(get_db())
            
            for key, data in indicators.items():
                # Desactivar indicadores anteriores del mismo tipo
                db.query(EconomicIndicator).filter(
                    EconomicIndicator.indicator_type == key,
                    EconomicIndicator.is_active == True
                ).update({"is_active": False})
                
                # Crear nuevo indicador
                indicator = EconomicIndicator(
                    indicator_type=key,
                    value=data["value"],
                    source=data["source"],
                    date=datetime.now(),
                    is_active=True
                )
                db.add(indicator)
            
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to save indicators to DB: {e}")
            raise
    
    async def _save_health_check(self):
        """Guarda health check en la base de datos"""
        try:
            db = next(get_db())
            
            health_check = HealthCheck(
                status=self.health.status,
                services=str(self.health.services),
                uptime_seconds=self.health.uptime_seconds,
                timestamp=self.health.last_check
            )
            db.add(health_check)
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to save health check: {e}")
    
    def get_status(self) -> Dict:
        """Obtiene el estado actual del scheduler"""
        return {
            "running": self.running,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "health": {
                "status": self.health.status,
                "services": self.health.services,
                "last_check": self.health.last_check.isoformat(),
                "error_count": self.health.error_count,
                "warning_count": self.health.warning_count
            },
            "tasks": {
                name: {
                    "status": task.status.value,
                    "last_run": task.last_run.isoformat() if task.last_run else None,
                    "next_run": task.next_run.isoformat(),
                    "error_count": task.error_count,
                    "enabled": task.enabled
                }
                for name, task in self.tasks.items()
            }
        }

# Singleton instance
scheduler = UnifiedScheduler()

# Convenience functions
async def start_scheduler():
    """Inicia el scheduler"""
    if settings.ENABLE_SCHEDULER:
        await scheduler.start()
    else:
        logger.info("Scheduler disabled in settings")

def stop_scheduler():
    """Detiene el scheduler"""
    scheduler.stop()

def get_scheduler_status():
    """Obtiene el estado del scheduler"""
    return scheduler.get_status()