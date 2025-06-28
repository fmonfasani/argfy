"""
Script de monitoreo continuo
Ejecutar: python scripts/monitor.py
"""
import time
import requests
import json
from datetime import datetime
import smtplib
from email.mime.text import MimeText
import os

class ArgfyMonitor:
    def __init__(self):
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self.alert_email = os.getenv("ALERT_EMAIL")
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        
    def check_backend_health(self):
        """Verificar salud del backend"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "data": data
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "down",
                "error": str(e)
            }
    
    def check_frontend_health(self):
        """Verificar salud del frontend"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "down",
                "error": str(e)
            }
    
    def check_api_endpoints(self):
        """Verificar endpoints críticos de la API"""
        endpoints = [
            "/api/v1/indicators/current",
            "/api/v1/indicators/news",
            "/api/v1/indicators/summary"
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                results[endpoint] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
            except Exception as e:
                results[endpoint] = {
                    "status": "down",
                    "error": str(e)
                }
        
        return results
    
    def send_alert(self, subject, message):
        """Enviar alerta por email"""
        if not all([self.alert_email, self.smtp_server, self.smtp_user, self.smtp_pass]):
            print(f"⚠️ ALERT: {subject} - {message}")
            return
        
        try:
            msg = MimeText(message)
            msg['Subject'] = f"🚨 Argfy Alert: {subject}"
            msg['From'] = self.smtp_user
            msg['To'] = self.alert_email
            
            with smtplib.SMTP(self.smtp_server, 587) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
                
            print(f"📧 Alert sent: {subject}")
        except Exception as e:
            print(f"❌ Failed to send alert: {e}")
    
    def run_monitoring_cycle(self):
        """Ejecutar un ciclo completo de monitoreo"""
        print(f"\n🔍 Monitoring cycle started at {datetime.now()}")
        
        # Verificar backend
        backend_health = self.check_backend_health()
        print(f"Backend: {backend_health['status']}")
        
        # Verificar frontend
        frontend_health = self.check_frontend_health()
        print(f"Frontend: {frontend_health['status']}")
        
        # Verificar endpoints de API
        api_results = self.check_api_endpoints()
        for endpoint, result in api_results.items():
            print(f"API {endpoint}: {result['status']}")
        
        # Alertas
        if backend_health['status'] != 'healthy':
            self.send_alert(
                "Backend Down", 
                f"Backend health check failed: {backend_health.get('error', 'Unknown error')}"
            )
        
        if frontend_health['status'] != 'healthy':
            self.send_alert(
                "Frontend Down", 
                f"Frontend health check failed: {frontend_health.get('error', 'Unknown error')}"
            )
        
        # Log completo
        monitoring_data = {
            "timestamp": datetime.now().isoformat(),
            "backend": backend_health,
            "frontend": frontend_health,
            "api_endpoints": api_results
        }
        
        # Guardar log
        with open("logs/monitoring.log", "a") as f:
            f.write(json.dumps(monitoring_data) + "\n")
    
    def run_continuous_monitoring(self, interval=300):  # 5 minutos
        """Ejecutar monitoreo continuo"""
        print(f"🔄 Starting continuous monitoring (interval: {interval}s)")
        
        while True:
            try:
                self.run_monitoring_cycle()
                print(f"✅ Monitoring cycle completed. Next check in {interval}s")
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute before retry

if __name__ == "__main__":
    # Crear directorio de logs
    os.makedirs("logs", exist_ok=True)
    
    monitor = ArgfyMonitor()
    
    # Ejecutar monitoreo
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        monitor.run_continuous_monitoring()
    else:
        monitor.run_monitoring_cycle()


