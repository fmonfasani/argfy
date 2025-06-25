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