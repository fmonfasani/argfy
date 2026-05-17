# backend/app/services/modern/bcra_httpx_service.py
# Servicio BCRA simplificado con httpx
import asyncio
from datetime import datetime
from typing import Dict
import logging

logger = logging.getLogger(__name__)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

class BCRAHTTPXService:
    """Servicio BCRA con httpx (con fallback)"""
    
    def __init__(self):
        self.base_url = "https://api.bcra.gob.ar"
        self.client = None
        
    async def __aenter__(self):
        if HTTPX_AVAILABLE:
            self.client = httpx.AsyncClient(timeout=10.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def get_exchange_rates(self) -> Dict:
        """Obtener cotizaciones con httpx"""
        if not HTTPX_AVAILABLE:
            return {"status": "error", "message": "httpx not available"}
        
        try:
            url = f"{self.base_url}/estadisticascambiarias/v1.0/Cotizaciones"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json(),
                    "timestamp": datetime.now().isoformat(),
                    "client_type": "httpx"
                }
            else:
                return {"status": "error", "code": response.status_code}
        except Exception as e:
            logger.error(f"Error httpx exchange rates: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_monetary_variables(self) -> Dict:
        """Obtener variables monetarias"""
        if not HTTPX_AVAILABLE:
            return {"status": "error", "message": "httpx not available"}
        
        try:
            url = f"{self.base_url}/estadisticas/v2.0/principalesvariables"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json(),
                    "timestamp": datetime.now().isoformat(),
                    "client_type": "httpx"
                }
            else:
                return {"status": "error", "code": response.status_code}
        except Exception as e:
            logger.error(f"Error httpx variables: {e}")
            return {"status": "error", "message": str(e)}

# Instancia global 
bcra_httpx_service = BCRAHTTPXService()
