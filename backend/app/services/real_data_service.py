# backend/app/services/real_data_service.py
import asyncio
import aiohttp
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class RealDataService:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        
    async def get_bcra_data(self) -> Dict:
        """Obtiene datos reales del BCRA"""
        try:
            # USD Oficial
            usd_oficial = await self._fetch_bcra_variable(1)
            
            # Reservas
            reservas = await self._fetch_bcra_variable(15)
            
            # Tasa de política
            tasa = await self._fetch_bcra_variable(7)
            
            return {
                "usd_oficial": usd_oficial,
                "reservas_bcra": reservas, 
                "tasa_bcra": tasa
            }
        except Exception as e:
            logger.error(f"Error fetching BCRA data: {e}")
            return {}
    
    async def get_dolar_blue(self) -> Optional[float]:
        """Obtiene cotización del dólar blue"""
        try:
            url = "https://api.bluelytics.com.ar/v2/latest"
            async with self.session.get(url) as response:
                data = await response.json()
                return data["blue"]["value_sell"]
        except Exception as e:
            logger.error(f"Error fetching dolar blue: {e}")
            return None
    
    async def get_inflation_data(self) -> Optional[float]:
        """Obtiene datos de inflación del INDEC"""
        try:
            # IPC Nacional
            url = "https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELNAL_DICI_M_26&limit=1"
            async with self.session.get(url) as response:
                data = await response.json()
                if data["data"]:
                    return data["data"][0][1]  # Último valor
        except Exception as e:
            logger.error(f"Error fetching inflation: {e}")
            return None
    
    async def get_riesgo_pais(self) -> Optional[int]:
        """Scraping del riesgo país"""
        # Implementar scraping de Ámbito o InfoBae
        # Por ahora retorna valor demo
        return 1642
    
    async def _fetch_bcra_variable(self, variable_id: int) -> Optional[float]:
        """Helper para obtener variables del BCRA"""
        try:
            url = f"https://api.bcra.gob.ar/estadisticas/v2.0/datosvariable/{variable_id}/2024-01-01/2024-12-31"
            async with self.session.get(url) as response:
                data = await response.json()
                if data.get("results"):
                    return data["results"][-1]["valor"]  # Último valor
        except Exception as e:
            logger.error(f"Error fetching BCRA variable {variable_id}: {e}")
            return None

# Uso en el router
real_data_service = RealDataService()