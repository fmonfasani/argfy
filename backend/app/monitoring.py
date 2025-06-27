# backend/app/monitoring.py
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import json

# Import psutil de forma opcional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil no disponible - algunas métricas de sistema deshabilitadas")

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requests"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"📥 {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log response
        logger.info(f"📤 {response.status_code} - {process_time:.4f}s")
        
        return response

class PerformanceMonitor:
    """Monitor de performance del sistema"""
    
    def __init__(self):
        self.requests_count = 0
        self.total_time = 0.0
        self.start_time = datetime.now()
        
    def record_request(self, duration: float):
        """Registrar tiempo de request"""
        self.requests_count += 1
        self.total_time += duration
    
    def get_system_metrics(self) -> Dict:
        """Obtener métricas del sistema"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "requests_total": self.requests_count,
            "avg_response_time": self.total_time / max(self.requests_count, 1),
        }
        
        # Agregar métricas de psutil solo si está disponible
        if PSUTIL_AVAILABLE:
            try:
                # CPU y memoria
                metrics.update({
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "memory_available_mb": psutil.virtual_memory().available / 1024 / 1024,
                    "disk_usage_percent": psutil.disk_usage('/').percent,
                })
            except Exception as e:
                logger.warning(f"Error obteniendo métricas psutil: {e}")
        else:
            # Métricas básicas sin psutil
            metrics.update({
                "cpu_percent": "N/A (psutil no disponible)",
                "memory_percent": "N/A (psutil no disponible)", 
                "memory_available_mb": "N/A (psutil no disponible)",
                "disk_usage_percent": "N/A (psutil no disponible)",
            })
        
        return metrics
    
    def get_health_status(self) -> Dict:
        """Estado de salud del sistema"""
        status = {
            "status": "healthy",
            "checks": {
                "uptime": "ok",
                "requests": "ok" if self.requests_count > 0 else "no_requests"
            }
        }
        
        # Checks adicionales con psutil
        if PSUTIL_AVAILABLE:
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_percent = psutil.virtual_memory().percent
                
                status["checks"].update({
                    "cpu": "ok" if cpu_percent < 80 else "high",
                    "memory": "ok" if memory_percent < 80 else "high"
                })
                
                # Estado general
                if cpu_percent > 90 or memory_percent > 90:
                    status["status"] = "degraded"
                    
            except Exception as e:
                status["checks"]["system_metrics"] = f"error: {e}"
        else:
            status["checks"]["system_metrics"] = "psutil_not_available"
        
        return status

# Instancia global del monitor
performance_monitor = PerformanceMonitor()

def get_performance_metrics() -> Dict:
    """Función helper para obtener métricas"""
    return performance_monitor.get_system_metrics()

def get_health_check() -> Dict:
    """Función helper para health check"""
    return performance_monitor.get_health_status()

# Función para verificar dependencias
def check_monitoring_dependencies() -> Dict:
    """Verificar qué dependencias están disponibles"""
    return {
        "psutil": PSUTIL_AVAILABLE,
        "monitoring_level": "full" if PSUTIL_AVAILABLE else "basic",
        "available_metrics": [
            "uptime", "requests_count", "avg_response_time"
        ] + (["cpu", "memory", "disk"] if PSUTIL_AVAILABLE else [])
    }