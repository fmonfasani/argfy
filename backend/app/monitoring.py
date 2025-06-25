# backend/app/monitoring.py
"""
Sistema de monitoreo y logging para Argfy
"""
import logging
import time
from datetime import datetime
from functools import wraps
from typing import Dict, Any
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import psutil
import asyncio

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/argfy.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requests"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"🔍 {request.method} {request.url.path} - {request.client.host}")
        
        response = await call_next(request)
        
        # Calcular tiempo de respuesta
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"✅ {request.method} {request.url.path} - "
            f"{response.status_code} - {process_time:.3f}s"
        )
        
        # Agregar header de tiempo de respuesta
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class PerformanceMonitor:
    """Monitor de performance del sistema"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        
    def log_request(self):
        """Registrar una request"""
        self.request_count += 1
        
    def log_error(self):
        """Registrar un error"""
        self.error_count += 1
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del sistema"""
        return {
            "uptime": str(datetime.now() - self.start_time),
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1) * 100,
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "timestamp": datetime.now().isoformat()
        }

# Instancia global del monitor
performance_monitor = PerformanceMonitor()

def log_performance(func_name: str = None):
    """Decorador para logging de performance"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = func_name or func.__name__
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"⚡ {function_name} completed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"❌ {function_name} failed in {execution_time:.3f}s: {str(e)}")
                performance_monitor.log_error()
                raise
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = func_name or func.__name__
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"⚡ {function_name} completed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"❌ {function_name} failed in {execution_time:.3f}s: {str(e)}")
                performance_monitor.log_error()
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

class HealthChecker:
    """Verificador de salud del sistema"""
    
    @staticmethod
    def check_database():
        """Verificar conexión a base de datos"""
        try:
            from .database import engine
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return {"status": "healthy", "message": "Database connection OK"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Database error: {str(e)}"}
    
    @staticmethod
    def check_external_apis():
        """Verificar APIs externas"""
        try:
            import requests
            response = requests.get("https://api.bcra.gob.ar", timeout=5)
            if response.status_code < 500:
                return {"status": "healthy", "message": "External APIs accessible"}
            else:
                return {"status": "degraded", "message": "External APIs slow"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"External API error: {str(e)}"}
    
    @staticmethod
    def get_health_status():
        """Obtener estado completo de salud"""
        checks = {
            "database": HealthChecker.check_database(),
            "external_apis": HealthChecker.check_external_apis(),
            "system_metrics": performance_monitor.get_system_metrics()
        }
        
        # Determinar estado general
        overall_status = "healthy"
        if any(check["status"] == "unhealthy" for check in checks.values()):
            overall_status = "unhealthy"
        elif any(check["status"] == "degraded" for check in checks.values()):
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "checks": checks
        }

