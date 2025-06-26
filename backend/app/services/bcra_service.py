# backend/app/services/bcra_real_service.py
import aiohttp
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BCRAVariable:
    id: int
    name: str
    description: str
    unit: str

class BCRARealService:
    """Servicio para obtener datos reales del BCRA"""
    
    BASE_URL = "https://api.bcra.gob.ar/estadisticas/v2.0"
    
    # Mapeo de variables importantes del BCRA
    VARIABLES = {
        'usd_oficial': BCRAVariable(1, 'USD Oficial', 'Tipo de cambio USD/ARS oficial', 'ARS'),
        'reservas': BCRAVariable(15, 'Reservas Internacionales', 'Reservas en millones USD', 'USD M'),
        'base_monetaria': BCRAVariable(25, 'Base Monetaria', 'Base monetaria total', 'ARS M'),
        'tasa_politica': BCRAVariable(7, 'Tasa de Política Monetaria', 'Tasa de referencia BCRA', '%'),
        'circulante': BCRAVariable(26, 'Circulación Monetaria', 'Billetes y monedas en circulación', 'ARS M'),
        'depositos': BCRAVariable(30, 'Depósitos Totales', 'Depósitos del sector privado', 'ARS M'),
        'creditos': BCRAVariable(31, 'Créditos Totales', 'Créditos al sector privado', 'ARS M'),
        'leliq': BCRAVariable(35, 'LELIQs', 'Stock de Letras de Liquidez', 'ARS M'),
    }
    
    def __init__(self):
        self.session = None
        self._cache = {}
        self._cache_ttl = 300  # 5 minutos
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_all_current_data(self) -> Dict[str, Any]:
        """Obtiene todos los datos actuales del BCRA"""
        try:
            current_data = {}
            
            # Ejecutar todas las consultas en paralelo
            tasks = []
            for key, variable in self.VARIABLES.items():
                task = self._get_variable_current(variable.id, key)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, dict):
                    current_data.update(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error in parallel fetch: {result}")
            
            # Agregar timestamp
            current_data['timestamp'] = datetime.now().isoformat()
            current_data['source'] = 'BCRA'
            
            return current_data
            
        except Exception as e:
            logger.error(f"Error fetching all BCRA data: {e}")
            return self._get_fallback_data()
    
    async def get_historical_data(self, variable_key: str, days: int = 30) -> List[Dict]:
        """Obtiene datos históricos de una variable específica"""
        if variable_key not in self.VARIABLES:
            raise ValueError(f"Variable {variable_key} no disponible")
        
        variable = self.VARIABLES[variable_key]
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            url = f"{self.BASE_URL}/datosvariable/{variable.id}/{start_date}/{end_date}"
            
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    historical_data = []
                    for item in data.get('results', []):
                        historical_data.append({
                            'date': item['fecha'],
                            'value': float(item['valor']),
                            'variable': variable_key,
                            'description': variable.description,
                            'unit': variable.unit
                        })
                    
                    return historical_data
                else:
                    logger.error(f"BCRA API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching historical data for {variable_key}: {e}")
            return []
    
    async def get_principal_variables(self) -> Dict[str, Any]:
        """Obtiene las principales variables económicas del BCRA"""
        try:
            url = f"{self.BASE_URL}/principalesvariables"
            
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    processed_data = {}
                    for item in data.get('results', []):
                        # Mapear a nombres más amigables
                        variable_name = self._map_principal_variable_name(item.get('descripcion', ''))
                        if variable_name:
                            processed_data[variable_name] = {
                                'value': float(item['valor']),
                                'date': item['fecha'],
                                'unit': self._extract_unit(item.get('descripcion', '')),
                                'description': item.get('descripcion', '')
                            }
                    
                    return processed_data
                else:
                    logger.error(f"Error fetching principal variables: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error in get_principal_variables: {e}")
            return {}
    
    async def _get_variable_current(self, variable_id: int, key: str) -> Dict[str, Any]:
        """Obtiene el valor actual de una variable específica"""
        cache_key = f"bcra_{variable_id}_{key}"
        
        # Check cache first
        if cache_key in self._cache:
            cache_time, cache_data = self._cache[cache_key]
            if (datetime.now() - cache_time).total_seconds() < self._cache_ttl:
                return cache_data
        
        try:
            # Obtener últimos 5 días para asegurar que tenemos datos
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
            
            url = f"{self.BASE_URL}/datosvariable/{variable_id}/{start_date}/{end_date}"
            
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get('results', [])
                    
                    if results:
                        latest = results[-1]  # Último dato disponible
                        result = {
                            key: {
                                'value': float(latest['valor']),
                                'date': latest['fecha'],
                                'variable_id': variable_id,
                                'source': 'BCRA'
                            }
                        }
                        
                        # Cache the result
                        self._cache[cache_key] = (datetime.now(), result)
                        return result
                        
                else:
                    logger.error(f"BCRA API error for variable {variable_id}: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error fetching variable {variable_id}: {e}")
        
        return {}
    
    def _map_principal_variable_name(self, description: str) -> Optional[str]:
        """Mapea descripciones del BCRA a nombres más amigables"""
        mapping = {
            'Reservas Internacionales del BCRA': 'reservas_bcra',
            'Base Monetaria': 'base_monetaria', 
            'Circulación Monetaria': 'circulante',
            'Tipo de Cambio de Referencia': 'usd_oficial',
            'Tasa de Política Monetaria': 'tasa_politica',
            'LELIQs': 'leliq_stock',
            'Depósitos': 'depositos_total'
        }
        
        for bcra_desc, friendly_name in mapping.items():
            if bcra_desc.lower() in description.lower():
                return friendly_name
        
        return None
    
    def _extract_unit(self, description: str) -> str:
        """Extrae la unidad de medida de la descripción"""
        if 'millones' in description.lower() and 'usd' in description.lower():
            return 'USD M'
        elif 'millones' in description.lower():
            return 'ARS M'
        elif '%' in description or 'tasa' in description.lower():
            return '%'
        elif 'tipo de cambio' in description.lower():
            return 'ARS'
        else:
            return ''
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Datos de fallback si el BCRA no está disponible"""
        return {
            'usd_oficial': {
                'value': 987.50,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'fallback'
            },
            'reservas': {
                'value': 21500.0,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'fallback'
            },
            'tasa_politica': {
                'value': 118.0,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'fallback'
            },
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback'
        }

# Función de conveniencia para uso síncrono
def get_bcra_data_sync() -> Dict[str, Any]:
    """Versión síncrona para uso en scripts o testing"""
    try:
        url = "https://api.bcra.gob.ar/estadisticas/v2.0/principalesvariables"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            processed = {}
            for item in data.get('results', []):
                if 'Reservas Internacionales' in item.get('descripcion', ''):
                    processed['reservas_bcra'] = float(item['valor'])
                elif 'Tipo de Cambio' in item.get('descripcion', ''):
                    processed['usd_oficial'] = float(item['valor'])
                elif 'Tasa de Política' in item.get('descripcion', ''):
                    processed['tasa_politica'] = float(item['valor'])
            
            return processed
        else:
            logger.error(f"BCRA sync API error: {response.status_code}")
            return {}
            
    except Exception as e:
        logger.error(f"Error in sync BCRA fetch: {e}")
        return {}

# Test function
async def test_bcra_service():
    """Función de test para el servicio BCRA"""
    async with BCRARealService() as service:
        print("🔄 Testing BCRA Real Service...")
        
        # Test 1: Datos actuales
        print("\n📊 Fetching current data...")
        current = await service.get_all_current_data()
        print(f"Current data keys: {list(current.keys())}")
        
        if 'usd_oficial' in current:
            usd = current['usd_oficial']
            print(f"USD Oficial: ${usd['value']} (fecha: {usd['date']})")
        
        # Test 2: Variables principales
        print("\n📈 Fetching principal variables...")
        principal = await service.get_principal_variables()
        print(f"Principal variables: {len(principal)} found")
        
        # Test 3: Datos históricos
        print("\n📜 Fetching historical data...")
        historical = await service.get_historical_data('usd_oficial', 7)
        print(f"Historical data points: {len(historical)}")
        
        if historical:
            latest = historical[-1]
            print(f"Latest USD: ${latest['value']} on {latest['date']}")
        
        print("\n✅ BCRA Service test completed!")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_bcra_service())