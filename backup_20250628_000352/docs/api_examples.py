"""
Ejemplos de uso de la API de Argfy
Ejecutar: python docs/api_examples.py
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"  # Cambiar por URL de producción
API_BASE = f"{BASE_URL}/api/v1"

def print_response(title, response):
    """Función helper para imprimir respuestas"""
    print(f"\n{'='*50}")
    print(f"📊 {title}")
    print(f"{'='*50}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"Error: {response.text}")

def example_current_indicators():
    """Ejemplo: Obtener indicadores actuales"""
    response = requests.get(f"{API_BASE}/indicators/current")
    print_response("Indicadores Actuales", response)
    return response.json() if response.status_code == 200 else None

def example_historical_data():
    """Ejemplo: Obtener datos históricos"""
    indicators = ["dolar_blue", "riesgo_pais", "inflacion_mensual"]
    
    for indicator in indicators:
        response = requests.get(f"{API_BASE}/indicators/historical/{indicator}?days=15")
        print_response(f"Datos Históricos - {indicator}", response)

def example_news():
    """Ejemplo: Obtener noticias"""
    response = requests.get(f"{API_BASE}/indicators/news?limit=3")
    print_response("Noticias Económicas", response)

def example_dashboard_summary():
    """Ejemplo: Obtener resumen del dashboard"""
    response = requests.get(f"{API_BASE}/indicators/summary")
    print_response("Resumen del Dashboard", response)

def example_refresh_data():
    """Ejemplo: Refrescar datos"""
    response = requests.post(f"{API_BASE}/indicators/refresh")
    print_response("Refresh de Datos", response)

def example_health_checks():
    """Ejemplo: Health checks"""
    endpoints = [
        ("/", "Endpoint Raíz"),
        ("/health", "Health Check"),
        ("/api/status", "API Status")
    ]
    
    for endpoint, title in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print_response(title, response)

if __name__ == "__main__":
    print("🚀 Ejemplos de API - Argfy Platform")
    print("===================================")
    
    try:
        # Health checks
        example_health_checks()
        
        # Indicadores
        example_current_indicators()
        
        # Datos históricos
        example_historical_data()
        
        # Noticias
        example_news()
        
        # Dashboard
        example_dashboard_summary()
        
        # Refresh
        example_refresh_data()
        
        print(f"\n{'='*50}")
        print("✅ Todos los ejemplos completados")
        print("📚 Documentación completa: http://localhost:8000/docs")
        print("🔄 ReDoc: http://localhost:8000/redoc")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print("   Asegúrate de que el backend esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")