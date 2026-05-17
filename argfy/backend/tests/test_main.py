# backend/tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import tempfile
import os

# Crear base de datos temporal para tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    # Crear tablas
    Base.metadata.create_all(bind=test_engine)
    yield
    # Limpiar después de tests
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("test.db"):
        os.remove("test.db")

def test_read_root(setup_database):
    """Test del endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Argfy API v0.1.0 - Demo Platform"
    assert data["status"] == "active"
    assert "endpoints" in data

def test_health_check(setup_database):
    """Test del health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "0.1.0"

def test_api_status(setup_database):
    """Test del status de la API"""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["api_version"] == "0.1.0"
    assert data["status"] == "operational"
    assert "services" in data
    assert "metrics" in data

def test_get_current_indicators(setup_database):
    """Test para obtener indicadores actuales"""
    response = client.get("/api/v1/indicators/current")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "timestamp" in data
    assert "status" in data
    assert data["status"] == "success"
    assert isinstance(data["data"], list)

def test_get_historical_data(setup_database):
    """Test para obtener datos históricos"""
    # Primero obtener indicadores para tener datos
    client.get("/api/v1/indicators/current")
    
    response = client.get("/api/v1/indicators/historical/dolar_blue?days=7")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "indicator" in data
    assert data["indicator"] == "dolar_blue"
    assert "period" in data
    assert data["status"] == "success"

def test_get_news(setup_database):
    """Test para obtener noticias"""
    response = client.get("/api/v1/indicators/news?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data
    assert data["status"] == "success"
    assert isinstance(data["data"], list)

def test_get_dashboard_summary(setup_database):
    """Test para obtener resumen del dashboard"""
    response = client.get("/api/v1/indicators/summary")
    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data
    assert "indicators" in data
    assert "news" in data
    assert data["status"] == "success"

def test_refresh_indicators(setup_database):
    """Test para refrescar indicadores"""
    response = client.post("/api/v1/indicators/refresh")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "timestamp" in data
    assert data["status"] == "success"

def test_invalid_endpoint(setup_database):
    """Test para endpoint inexistente"""
    response = client.get("/api/v1/invalid")
    assert response.status_code == 404

def test_historical_data_invalid_indicator(setup_database):
    """Test para indicador inválido en datos históricos"""
    response = client.get("/api/v1/indicators/historical/invalid_indicator")
    assert response.status_code == 200  # Debería retornar datos vacíos, no error
    data = response.json()
    assert data["indicator"] == "invalid_indicator"

# backend/docs/api_examples.py
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

# docs/API_GUIDE.md - Documentación extendida de la API
"""
# 📚 Guía Completa de la API de Argfy

## Introducción

La API de Argfy proporciona acceso a datos económicos argentinos en tiempo real. 
Esta guía incluye ejemplos prácticos y casos de uso comunes.

## Autenticación

**Demo v0.1**: No requiere autenticación
**Producción**: API Keys (próximamente)

## Endpoints Principales

### 1. Indicadores Actuales

**GET** `/api/v1/indicators/current`

Retorna todos los indicadores económicos actuales.

**Respuesta:**
```json
{
  "data": [
    {
      "id": 1,
      "indicator_type": "dolar_blue",
      "value": 1047.0,
      "date": "2024-06-25T10:00:00",
      "source": "demo",
      "is_active": true
    }
  ],
  "timestamp": "2024-06-25T10:00:00",
  "count": 8,
  "status": "success"
}
```

### 2. Datos Históricos

**GET** `/api/v1/indicators/historical/{indicator_type}?days={days}`

**Parámetros:**
- `indicator_type`: Tipo de indicador (dolar_blue, inflacion_mensual, etc.)
- `days`: Número de días (1-365, default: 30)

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/indicators/historical/dolar_blue?days=7"
```

### 3. Noticias

**GET** `/api/v1/indicators/news?limit={limit}&category={category}`

**Parámetros:**
- `limit`: Número de noticias (1-20, default: 6)
- `category`: Categoría opcional (ECONOMÍA, MERCADOS, etc.)

### 4. Resumen del Dashboard

**GET** `/api/v1/indicators/summary`

Retorna datos combinados de indicadores y noticias para el dashboard.

## Códigos de Estado

- `200`: Éxito
- `404`: Endpoint no encontrado
- `422`: Error de validación de parámetros
- `500`: Error interno del servidor

## Límites y Throttling

**Demo v0.1**: Sin límites
**Producción**: 1000 requests/hour por API key

## SDKs y Bibliotecas

### Python
```python
import requests

class ArgfyAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
    
    def get_indicators(self):
        response = requests.get(f"{self.api_base}/indicators/current")
        return response.json()
    
    def get_historical(self, indicator, days=30):
        response = requests.get(f"{self.api_base}/indicators/historical/{indicator}?days={days}")
        return response.json()

# Uso
api = ArgfyAPI()
indicators = api.get_indicators()
```

### JavaScript/Node.js
```javascript
class ArgfyAPI {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.apiBase = `${baseUrl}/api/v1`;
  }

  async getIndicators() {
    const response = await fetch(`${this.apiBase}/indicators/current`);
    return response.json();
  }

  async getHistorical(indicator, days = 30) {
    const response = await fetch(`${this.apiBase}/indicators/historical/${indicator}?days=${days}`);
    return response.json();
  }
}

// Uso
const api = new ArgfyAPI();
const indicators = await api.getIndicators();
```

## Casos de Uso Comunes

### 1. Dashboard de Trading
```python
# Obtener datos para dashboard
indicators = api.get_indicators()
dolar_blue = next(i for i in indicators['data'] if i['indicator_type'] == 'dolar_blue')
historical = api.get_historical('dolar_blue', 30)

print(f"Dólar Blue actual: ${dolar_blue['value']}")
```

### 2. Alertas de Precios
```python
# Monitorear cambios en el dólar blue
def check_dollar_alert(threshold=1050):
    indicators = api.get_indicators()
    dolar = next(i for i in indicators['data'] if i['indicator_type'] == 'dolar_blue')
    
    if dolar['value'] > threshold:
        send_alert(f"🚨 Dólar Blue: ${dolar['value']}")
```

### 3. Análisis de Tendencias
```python
# Analizar tendencia de inflación
historical = api.get_historical('inflacion_mensual', 90)
values = [point['value'] for point in historical['data']]
trend = 'UP' if values[-1] > values[0] else 'DOWN'
```

## Webhooks (Próximamente)

Los webhooks permitirán recibir notificaciones automáticas cuando cambien los indicadores.

```json
{
  "event": "indicator_updated",
  "data": {
    "indicator_type": "dolar_blue",
    "old_value": 1045.0,
    "new_value": 1047.0,
    "timestamp": "2024-06-25T10:00:00"
  }
}
```

## Soporte

- **Documentación interactiva**: `/docs`
- **ReDoc**: `/redoc`
- **Email**: contact@argfy.com
- **GitHub Issues**: Para reportar bugs

---

*Última actualización: Demo v0.1*
"""