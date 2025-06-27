# backend/app/services/performance/bcra_massive_service.py
# Servicio de concurrencia masiva con aiohttp
import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class BCRAMassiveService:
    """Servicio para concurrencia masiva con aiohttp"""
    
    def __init__(self):
        self.base_url = "https://api.bcra.gob.ar"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_all_variables_massive(self) -> Dict:
        """Obtener TODAS las variables BCRA en paralelo masivo"""
        try:
            # Crear tareas paralelas para variables principales
            tasks = []
            main_variables = [1, 4, 5, 6, 7, 15, 25, 27, 28, 34]  # Variables clave
ECHO est  desactivado.
            for var_id in main_variables:
                url = f"{self.base_url}/estadisticas/v2.0/datosvariable/{var_id}/2024-01-01/2024-12-31"
                task = self.session.get(url)
                tasks.append(task)
ECHO est  desactivado.
            # Ejecutar en paralelo
            responses = await asyncio.gather(*tasks, return_exceptions=True)
ECHO est  desactivado.
            # Procesar resultados
            successful = 0
            failed = 0
            data = []
ECHO est  desactivado.
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    failed += 1
                    logger.error(f"Error variable {main_variables[i]}: {response}")
                else:
                    try:
                        if response.status == 200:
                            json_data = await response.json()
                            data.append({
                                "variable_id": main_variables[i],
                                "data": json_data
                            })
                            successful += 1
                        else:
                            failed += 1
                            logger.error(f"HTTP {response.status} for variable {main_variables[i]}")
                    except Exception as parse_error:
                        failed += 1
                        logger.error(f"Parse error variable {main_variables[i]}: {parse_error}")
                    finally:
                        response.close()
ECHO est  desactivado.
            return {
                "status": "success",
                "total_requested": len(main_variables),
                "successful": successful,
                "failed": failed,
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "client_type": "aiohttp_massive"
            }
        
        except Exception as e:
            logger.error(f"Error massive aiohttp: {e}")
            return {"status": "error", "message": str(e)}

# Instancia global
bcra_massive_service = BCRAMassiveService()
