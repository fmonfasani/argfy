# app/services/bcra_service.py - Versión sin pandas
import requests
import random
from datetime import datetime, timedelta

class BCRAService:
    BASE_URL = "https://api.bcra.gob.ar"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_exchange_rate(self):
        """Obtiene cotización USD oficial del BCRA"""
        try:
            endpoint = f"{self.BASE_URL}/estadisticas/v2.0/datosvariable/1/2023-01-01/2024-12-31"
            response = self.session.get(endpoint, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
        except Exception as e:
            print(f"Error fetching BCRA data: {e}")
            return []
    
    def get_reserves(self):
        """Obtiene reservas internacionales"""
        try:
            endpoint = f"{self.BASE_URL}/estadisticas/v2.0/datosvariable/15/2023-01-01/2024-12-31"
            response = self.session.get(endpoint, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
        except Exception as e:
            print(f"Error fetching reserves data: {e}")
            return []

def generate_demo_data():
    """Genera datos de demo para la plataforma"""
    base_date = datetime.now()
    
    demo_indicators = [
        {
            "indicator_type": "dolar_blue",
            "value": 1047.0 + random.uniform(-20, 20),
            "source": "demo",
            "date": base_date
        },
        {
            "indicator_type": "dolar_oficial", 
            "value": 987.50 + random.uniform(-10, 10),
            "source": "BCRA",
            "date": base_date
        },
        {
            "indicator_type": "dolar_mep",
            "value": 1023.75 + random.uniform(-15, 15), 
            "source": "MEP",
            "date": base_date
        },
        {
            "indicator_type": "inflacion_mensual",
            "value": 4.2 + random.uniform(-0.5, 0.5),
            "source": "INDEC",
            "date": base_date
        },
        {
            "indicator_type": "reservas_bcra",
            "value": 21500.0 + random.uniform(-500, 500),
            "source": "BCRA", 
            "date": base_date
        },
        {
            "indicator_type": "riesgo_pais",
            "value": 1642.0 + random.uniform(-50, 50),
            "source": "JP Morgan",
            "date": base_date
        },
        {
            "indicator_type": "tasa_bcra",
            "value": 118.0,
            "source": "BCRA",
            "date": base_date
        },
        {
            "indicator_type": "merval",
            "value": 1456234 + random.uniform(-10000, 10000),
            "source": "BYMA",
            "date": base_date
        }
    ]
    
    return demo_indicators

def generate_historical_data(indicator_type: str, days: int = 30):
    """Genera datos históricos simulados"""
    historical_data = []
    base_values = {
        "dolar_blue": 1047.0,
        "dolar_oficial": 987.5, 
        "inflacion_mensual": 4.2,
        "reservas_bcra": 21500.0,
        "riesgo_pais": 1642.0,
        "merval": 1456234
    }
    
    base_value = base_values.get(indicator_type, 100.0)
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        # Simulación de variación diaria
        variation = random.uniform(-0.02, 0.02)  # ±2% diario
        value = base_value * (1 + variation * (i / days))
        
        historical_data.append({
            "indicator_id": indicator_type,
            "value": value,
            "date": date,
            "period": "daily",
            "source": "demo"
        })
    
    return historical_data

def generate_demo_news():
    """Genera noticias de demo"""
    news_items = [
        {
            "title": "BCRA mantiene la tasa de interés en 118%",
            "summary": "El banco central decidió mantener sin cambios la tasa de política monetaria en su última reunión...",
            "category": "ECONOMÍA",
            "source": "Argfy News",
            "published_at": datetime.now() - timedelta(hours=2),
            "is_featured": True
        },
        {
            "title": "Merval cierra con suba del 2.1%", 
            "summary": "El índice principal de la Bolsa porteña registró una jornada positiva impulsada por los papeles financieros...",
            "category": "MERCADOS",
            "source": "Argfy News",
            "published_at": datetime.now() - timedelta(hours=4)
        },
        {
            "title": "Soja alcanza US$485 por tonelada",
            "summary": "Los precios de la oleaginosa se mantienen firmes en el mercado internacional impulsados por la demanda...", 
            "category": "COMMODITIES",
            "source": "Argfy News",
            "published_at": datetime.now() - timedelta(hours=6)
        }
    ]
    
    return news_items
