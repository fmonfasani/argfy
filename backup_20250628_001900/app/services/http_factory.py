# backend/app/services/http_factory.py
# Factory inteligente para seleccionar la mejor librería HTTP
import logging
from typing import Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)

class ClientType(Enum):
    REQUESTS = "requests"
    HTTPX = "httpx" 
    AIOHTTP = "aiohttp"

class HTTPClientFactory:
    """Factory para auto-seleccionar la mejor librería HTTP"""
    
    # Detectar librerías disponibles
    _capabilities = {}
    
    @classmethod
    def _detect_capabilities(cls):
        """Detectar qué librerías están disponibles"""
        if cls._capabilities:
            return cls._capabilities
        
        # requests siempre disponible
        cls._capabilities["requests"] = True
        
        # httpx
        try:
            import httpx
            cls._capabilities["httpx"] = True
            logger.info("✅ httpx disponible")
        except ImportError:
            cls._capabilities["httpx"] = False
            logger.warning("⚠️  httpx no disponible")
        
        # aiohttp
        try:
            import aiohttp
            cls._capabilities["aiohttp"] = True
            logger.info("✅ aiohttp disponible")
        except ImportError:
            cls._capabilities["aiohttp"] = False
            logger.warning("⚠️  aiohttp no disponible")
        
        return cls._capabilities
    
    @classmethod
    def get_best_client(cls, use_case: str):
        """Obtener el mejor cliente para un caso de uso"""
        caps = cls._detect_capabilities()
        
        if use_case == "scraping":
            # Para scraping, requests es lo mejor
            import requests
            return requests.Session(), ClientType.REQUESTS
            
        elif use_case == "massive_parallel":
            # Para concurrencia masiva, aiohttp primero
            if caps["aiohttp"]:
                import aiohttp
                return aiohttp.ClientSession, ClientType.AIOHTTP
            elif caps["httpx"]:
                import httpx
                return httpx.AsyncClient, ClientType.HTTPX
            else:
                import requests
                return requests.Session(), ClientType.REQUESTS
                
        elif use_case == "modern_api":
            # Para APIs modernas, httpx primero
            if caps["httpx"]:
                import httpx
                return httpx.AsyncClient, ClientType.HTTPX
            elif caps["aiohttp"]:
                import aiohttp  
                return aiohttp.ClientSession, ClientType.AIOHTTP
            else:
                import requests
                return requests.Session(), ClientType.REQUESTS
                
        else:
            # Default: httpx si está disponible, sino requests
            if caps["httpx"]:
                import httpx
                return httpx.AsyncClient, ClientType.HTTPX
            else:
                import requests
                return requests.Session(), ClientType.REQUESTS
    
    @classmethod
    def get_capabilities(cls):
        """Obtener capacidades disponibles"""
        return cls._detect_capabilities()
