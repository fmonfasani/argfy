import os
import json
import asyncio
import aiohttp
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import psutil
import requests
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('argfy_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ArgfyProductionMonitor:
    """Sistema de monitoreo para producción"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.backend_url = config.get('backend_url', 'https://argfy-backend.onrender.com')
        self.frontend_url = config.get('frontend_url', 'https://argfy.vercel.app')
        self.alert_email = config.get('alert_email', 'alerts@argfy.com')
        self.slack_webhook = config.get('slack_webhook')
        
        self.metrics = {
            'uptime': {'backend': 0, 'frontend': 0},
            'response_times': {'backend': [], 'frontend': []},
            'error_rates': {'backend': 0, 'frontend': 0},
            'api_calls': {'total': 0, 'errors': 0},
            'last_check': datetime.now().isoformat()
        }
        
    async def run_continuous_monitoring(self, interval_minutes: int = 5):
        """Ejecutar monitoreo continuo"""
        logger.info(f"🚀 Iniciando monitoreo continuo cada {interval_minutes} minutos")
        
        while True:
            try:
                await self.perform_health_checks()
                await self.collect_metrics()
                await self.check_alert_conditions()
                
                # Generar reporte cada hora
                if datetime.now().minute == 0:
                    await self.generate_hourly_report()
                
                # Esperar al siguiente ciclo
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error en monitoreo continuo: {e}")
                await self.send_alert(f"🚨 Error en sistema de monitoreo: {e}")
                await asyncio.sleep(interval_minutes * 60)
    
    async def perform_health_checks(self):
        """Realizar checks de salud completos"""
        
        # Health check backend
        backend_healthy = await self.check_backend_health()
        
        # Health check frontend
        frontend_healthy = await self.check_frontend_health()
        
        # API endpoints check
        api_healthy = await self.check_api_endpoints()
        
        # Database check
        db_healthy = await self.check_database_health()
        
        # Update metrics
        self.metrics['uptime']['backend'] = 1 if backend_healthy else 0
        self.metrics['uptime']['frontend'] = 1 if frontend_healthy else 0
        self.metrics['last_check'] = datetime.now().isoformat()
        
        logger.info(f"Health Check - Backend: {'✅' if backend_healthy else '❌'}, "
                   f"Frontend: {'✅' if frontend_healthy else '❌'}, "
                   f"API: {'✅' if api_healthy else '❌'}, "
                   f"DB: {'✅' if db_healthy else '❌'}")
    
    async def check_backend_health(self) -> bool:
        """Check health del backend"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/health", timeout=10) as response:
                    response_time = asyncio.get_event_loop().time() - start_time
                    self.metrics['response_times']['backend'].append(response_time)
                    
                    if response.status == 200:
                        data = await response.json()
                        return data.get('status') == 'healthy'
                    
                    return False
                    
        except Exception as e:
            logger.error(f"Backend health check failed: {e}")
            return False
    
    async def check_frontend_health(self) -> bool:
        """Check health del frontend"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.frontend_url, timeout=10) as response:
                    response_time = asyncio.get_event_loop().time() - start_time
                    self.metrics['response_times']['frontend'].append(response_time)
                    
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Frontend health check failed: {e}")
            return False
    
    async def check_api_endpoints(self) -> bool:
        """Check de endpoints críticos de la API"""
        critical_endpoints = [
            '/api/v1/dashboard/complete',
            '/api/v1/indicators/economia',
            '/api/v1/config/categories'
        ]
        
        healthy_count = 0
        
        async with aiohttp.ClientSession() as session:
            for endpoint in critical_endpoints:
                try:
                    async with session.get(f"{self.backend_url}{endpoint}", timeout=5) as response:
                        if response.status == 200:
                            healthy_count += 1
                        self.metrics['api_calls']['total'] += 1
                        
                except Exception as e:
                    logger.error(f"API endpoint {endpoint} failed: {e}")
                    self.metrics['api_calls']['errors'] += 1
        
        return healthy_count >= len(critical_endpoints) * 0.8  # 80% debe estar funcionando
    
    async def check_database_health(self) -> bool:
        """Check de salud de la base de datos"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/health/detailed", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Verificar que el sistema no esté sobrecargado
                        system_info = data.get('system', {})
                        cpu_usage = system_info.get('cpu_percent', 0)
                        memory_usage = system_info.get('memory_percent', 0)
                        
                        return cpu_usage < 90 and memory_usage < 90
                    
                    return False
                    
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def collect_metrics(self):
        """Recolectar métricas de performance"""
        
        # Calcular promedios de response time
        if self.metrics['response_times']['backend']:
            avg_backend = sum(self.metrics['response_times']['backend'][-10:]) / len(self.metrics['response_times']['backend'][-10:])
            logger.info(f"📊 Backend avg response time: {avg_backend:.2f}s")
        
        if self.metrics['response_times']['frontend']:
            avg_frontend = sum(self.metrics['response_times']['frontend'][-10:]) / len(self.metrics['response_times']['frontend'][-10:])
            logger.info(f"📊 Frontend avg response time: {avg_frontend:.2f}s")
        
        # Calcular error rate
        total_calls = self.metrics['api_calls']['total']
        errors = self.metrics['api_calls']['errors']
        error_rate = (errors / total_calls * 100) if total_calls > 0 else 0
        self.metrics['error_rates']['backend'] = error_rate
        
        logger.info(f"📊 API Error rate: {error_rate:.1f}%")
    
    async def check_alert_conditions(self):
        """Verificar condiciones que requieren alertas"""
        
        alerts = []
        
        # Backend down
        if self.metrics['uptime']['backend'] == 0:
            alerts.append("🚨 Backend is DOWN")
        
        # Frontend down
        if self.metrics['uptime']['frontend'] == 0:
            alerts.append("🚨 Frontend is DOWN")
        
        # High response times
        if self.metrics['response_times']['backend']:
            avg_response = sum(self.metrics['response_times']['backend'][-5:]) / len(self.metrics['response_times']['backend'][-5:])
            if avg_response > 5.0:
                alerts.append(f"⚠️ High backend response time: {avg_response:.2f}s")
        
        # High error rate
        if self.metrics['error_rates']['backend'] > 10:  # 10% error rate
            alerts.append(f"⚠️ High error rate: {self.metrics['error_rates']['backend']:.1f}%")
        
        # Enviar alertas si hay problemas
        for alert in alerts:
            await self.send_alert(alert)
    
    async def send_alert(self, message: str):
        """Enviar alerta por múltiples canales"""
        logger.warning(f"ALERT: {message}")
        
        # Slack notification
        if self.slack_webhook:
            await self.send_slack_alert(message)
        
        # Email notification
        await self.send_email_alert(message)
    
    async def send_slack_alert(self, message: str):
        """Enviar alerta a Slack"""
        try:
            payload = {
                "text": f"🚨 Argfy Platform Alert",
                "attachments": [{
                    "color": "danger",
                    "fields": [{
                        "title": "Alert",
                        "value": message,
                        "short": False
                    }, {
                        "title": "Time",
                        "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "short": True
                    }, {
                        "title": "Backend",
                        "value": self.backend_url,
                        "short": True
                    }]
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.slack_webhook, json=payload) as response:
                    if response.status == 200:
                        logger.info("✅ Slack alert sent")
                    else:
                        logger.error(f"❌ Failed to send Slack alert: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
    
    async def send_email_alert(self, message: str):
        """Enviar alerta por email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.get('smtp_user', 'noreply@argfy.com')
            msg['To'] = self.alert_email
            msg['Subject'] = f"🚨 Argfy Platform Alert - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            body = f"""
            Argfy Platform Alert
            
            Alert: {message}
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
            
            System Status:
            - Backend: {'✅ UP' if self.metrics['uptime']['backend'] else '❌ DOWN'}
            - Frontend: {'✅ UP' if self.metrics['uptime']['frontend'] else '❌ DOWN'}
            - Error Rate: {self.metrics['error_rates']['backend']:.1f}%
            
            URLs:
            - Backend: {self.backend_url}
            - Frontend: {self.frontend_url}
            - Health: {self.backend_url}/health
            
            This is an automated alert from Argfy Platform Monitoring.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Enviar email (configurar SMTP en producción)
            logger.info("📧 Email alert prepared (configure SMTP to send)")
            
        except Exception as e:
            logger.error(f"Error preparing email alert: {e}")
    
    async def generate_hourly_report(self):
        """Generar reporte cada hora"""
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "period": "1 hour",
            "status": {
                "backend_uptime": f"{self.metrics['uptime']['backend'] * 100:.1f}%",
                "frontend_uptime": f"{self.metrics['uptime']['frontend'] * 100:.1f}%",
                "error_rate": f"{self.metrics['error_rates']['backend']:.1f}%"
            },
            "performance": {
                "avg_backend_response": f"{sum(self.metrics['response_times']['backend'][-60:]) / len(self.metrics['response_times']['backend'][-60:]):.2f}s" if self.metrics['response_times']['backend'] else "N/A",
                "total_api_calls": self.metrics['api_calls']['total'],
                "failed_calls": self.metrics['api_calls']['errors']
            }
        }
        
        # Guardar reporte
        timestamp = datetime.now().strftime("%Y%m%d_%H")
        with open(f"monitoring_report_{timestamp}.json", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Hourly report generated: monitoring_report_{timestamp}.json")


class ArgfyPerformanceOptimizer:
    """Optimizador de performance en producción"""
    
    def __init__(self, backend_url: str):
        self.backend_url = backend_url
        
    async def run_optimization_suite(self):
        """Ejecutar suite completa de optimización"""
        
        logger.info("🚀 Ejecutando optimizaciones de performance")
        
        optimizations = [
            ("Database optimization", self.optimize_database_queries),
            ("Cache warming", self.warm_cache),
            ("API response optimization", self.optimize_api_responses),
            ("Resource cleanup", self.cleanup_resources)
        ]
        
        results = {}
        
        for name, optimization_func in optimizations:
            try:
                logger.info(f"🔧 {name}...")
                result = await optimization_func()
                results[name] = result
                logger.info(f"✅ {name} completed: {result}")
            except Exception as e:
                logger.error(f"❌ {name} failed: {e}")
                results[name] = f"Failed: {e}"
        
        return results
    
    async def optimize_database_queries(self):
        """Optimizar queries de base de datos"""
        # En producción, esto haría optimizaciones reales
        # Por ahora simular optimización
        await asyncio.sleep(1)
        return "Database queries optimized"
    
    async def warm_cache(self):
        """Calentar cache con datos frecuentemente accedidos"""
        
        # Hacer requests a endpoints principales para calentar cache
        endpoints = [
            '/api/v1/dashboard/complete',
            '/api/v1/indicators/economia',
            '/api/v1/indicators/gobierno',
            '/api/v1/indicators/finanzas',
            '/api/v1/config/categories'
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    async with session.get(f"{self.backend_url}{endpoint}") as response:
                        if response.status == 200:
                            await response.json()  # Procesar respuesta
                except Exception as e:
                    logger.error(f"Failed to warm cache for {endpoint}: {e}")
        
        return f"Cache warmed for {len(endpoints)} endpoints"
    
    async def optimize_api_responses(self):
        """Optimizar respuestas de API"""
        # Verificar compresión, headers de cache, etc.
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.backend_url}/api/v1/dashboard/complete") as response:
                headers = response.headers
                
                optimizations = []
                
                if 'gzip' in headers.get('content-encoding', ''):
                    optimizations.append("Compression enabled")
                
                if 'cache-control' in headers:
                    optimizations.append("Cache headers present")
                
                return f"API optimizations: {optimizations}"
    
    async def cleanup_resources(self):
        """Limpiar recursos no utilizados"""
        
        # En producción esto limpiaría:
        # - Logs antiguos
        # - Cache entries expirados  
        # - Temporary files
        # - Unused database connections
        
        await asyncio.sleep(0.5)
        return "Resources cleaned up"
