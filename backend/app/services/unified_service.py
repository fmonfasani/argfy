# backend/app/services/unified_service.py
# Servicio unificado que usa la mejor librería para cada caso
from .http_factory import HTTPClientFactory
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class UnifiedEconomicService:
    """Servicio unificado que selecciona automáticamente la mejor librería"""
    
    def __init__(self):
        self.capabilities = HTTPClientFactory.get_capabilities()
        logger.info(f"Capacidades HTTP: {self.capabilities}")
        
    async def get_dollar_data(self) -> Dict:
        """Obtener datos del dólar usando la mejor estrategia"""
        results = {}
        
        # 1. Scraping con requests (si beautifulsoup4 está disponible)
        try:
            from .base.scraping_service import scraping_service
            ambito_data = scraping_service.get_ambito_dollar()
            if ambito_data:
                results["ambito"] = ambito_data
            
            cronista_data = scraping_service.get_cronista_dollar()
            if cronista_data:
                results["cronista"] = cronista_data
        except Exception as e:
            logger.error(f"Error scraping dollar: {e}")
        
        # 2. APIs modernas con httpx
        if self.capabilities.get("httpx"):
            try:
                from .modern.bcra_httpx_service import bcra_httpx_service
                async with bcra_httpx_service as service:
                    bcra_data = await service.get_exchange_rates()
                    if bcra_data.get("status") == "success":
                        results["bcra_httpx"] = bcra_data
            except Exception as e:
                logger.error(f"Error httpx dollar data: {e}")
        
        return {
            "status": "success",
            "sources": list(results.keys()),
            "data": results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_massive_bcra_data(self) -> Dict:
        """Obtener datos masivos usando la mejor estrategia disponible"""
        
        # Si aiohttp está disponible, usar concurrencia masiva
        if self.capabilities.get("aiohttp"):
            try:
                from .performance.bcra_massive_service import bcra_massive_service
                async with bcra_massive_service as service:
                    return await service.get_all_variables_massive()
            except Exception as e:
                logger.error(f"Error aiohttp massive: {e}")
        
        # Fallback a httpx
        elif self.capabilities.get("httpx"):
            try:
                from .modern.bcra_httpx_service import bcra_httpx_service
                async with bcra_httpx_service as service:
                    return await service.get_monetary_variables()
            except Exception as e:
                logger.error(f"Error httpx fallback: {e}")
        
        # Último fallback: requests
        import requests
        try:
            response = requests.get("https://api.bcra.gob.ar/estadisticas/v2.0/principalesvariables", timeout=10)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json(),
                    "client_type": "requests_fallback",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error requests fallback: {e}")
        
        return {"status": "error", "message": "All HTTP methods failed"}

# Instancia global
unified_service = UnifiedEconomicService()
