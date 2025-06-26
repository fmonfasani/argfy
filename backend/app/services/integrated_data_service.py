# backend/app/services/integrated_data_service.py
"""
Servicio integrado que combina todas las fuentes de datos reales para Argfy Platform
Reemplaza los datos demo con datos reales de múltiples APIs
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
import json
import os

# Import our custom services
from .bcra_real_service import BCRARealService
from .dolar_blue_service import DolarBlueService

logger = logging.getLogger(__name__)

@dataclass
class EconomicData:
    """Estructura unificada para datos económicos"""
    indicator_type: str
    value: float
    date: datetime
    source: str
    unit: str = ""
    metadata: Dict = None
    
    def to_indicator_dict(self):
        """Convierte a formato EconomicIndicator para la DB"""
        return {
            'indicator_type': self.indicator_type,
            'value': self.value,
            'date': self.date,
            'source': self.source,
            'is_active': True,
            'metadata_info': json.dumps(self.metadata or {})
        }

class IntegratedDataService:
    """Servicio principal que integra todas las fuentes de datos reales"""
    
    def __init__(self):
        self.bcra_service = None
        self.dolar_service = None
        self.session = None
        self._cache = {}
        self._cache_ttl = 300  # 5 minutos cache general
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        self.bcra_service = BCRARealService()
        await self.bcra_service.__aenter__()
        self.dolar_service = DolarBlueService()
        await self.dolar_service.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.bcra_service:
            await self.bcra_service.__aexit__(exc_type, exc_val, exc_tb)
        if self.dolar_service:
            await self.dolar_service.__aexit__(exc_type, exc_val, exc_tb)
        if self.session:
            await self.session.close()
    
    async def get_all_current_indicators(self) -> List[EconomicData]:
        """Obtiene todos los indicadores actuales de todas las fuentes"""
        indicators = []
        
        try:
            # 1. Datos del BCRA (USD oficial, reservas, tasa, etc.)
            bcra_data = await self._fetch_bcra_indicators()
            indicators.extend(bcra_data)
            
            # 2. Cotizaciones dólar (blue, MEP, CCL)
            dolar_data = await self._fetch_dolar_indicators()
            indicators.extend(dolar_data)
            
            # 3. Datos de inflación (INDEC)
            inflation_data = await self._fetch_inflation_indicators()
            indicators.extend(inflation_data)
            
            # 4. Riesgo país (scraping)
            riesgo_data = await self._fetch_riesgo_pais()
            if riesgo_data:
                indicators.append(riesgo_data)
            
            # 5. Datos de mercado (MERVAL, etc.)
            market_data = await self._fetch_market_indicators()
            indicators.extend(market_data)
            
            logger.info(f"Fetched {len(indicators)} real indicators")
            return indicators
            
        except Exception as e:
            logger.error(f"Error fetching all indicators: {e}")
            return self._get_fallback_indicators()
    
    async def _fetch_bcra_indicators(self) -> List[EconomicData]:
        """Obtiene indicadores del BCRA"""
        indicators = []
        
        try:
            bcra_data = await self.bcra_service.get_all_current_data()
            
            # Mapear datos del BCRA a nuestro formato
            mapping = {
                'usd_oficial': ('dolar_oficial', 'ARS'),
                'reservas': ('reservas_bcra', 'USD M'),
                'tasa_politica': ('tasa_bcra', '%'),
                'base_monetaria': ('base_monetaria', 'ARS M'),
                'circulante': ('circulante', 'ARS M'),
                'leliq': ('leliq_stock', 'ARS M')
            }
            
            for bcra_key, (our_key, unit) in mapping.items():
                if bcra_key in bcra_data:
                    data = bcra_data[bcra_key]
                    indicators.append(EconomicData(
                        indicator_type=our_key,
                        value=data['value'],
                        date=datetime.fromisoformat(data['date']),
                        source='BCRA',
                        unit=unit,
                        metadata={'variable_id': data.get('variable_id')}
                    ))
            
        except Exception as e:
            logger.error(f"Error fetching BCRA indicators: {e}")
        
        return indicators
    
    async def _fetch_dolar_indicators(self) -> List[EconomicData]:
        """Obtiene cotizaciones del dólar de múltiples fuentes"""
        indicators = []
        
        try:
            all_rates = await self.dolar_service.get_all_rates()
            
            # Mapear cotizaciones a indicadores
            for rate_key, rate in all_rates.items():
                # Usar precio de venta como valor principal
                indicators.append(EconomicData(
                    indicator_type=f'dolar_{rate_key}',
                    value=rate.sell,
                    date=rate.timestamp,
                    source=rate.source,
                    unit='ARS',
                    metadata={
                        'buy_price': rate.buy,
                        'sell_price': rate.sell,
                        'spread': round(rate.sell - rate.buy, 2)
                    }
                ))
            
        except Exception as e:
            logger.error(f"Error fetching dolar indicators: {e}")
        
        return indicators
    
    async def _fetch_inflation_indicators(self) -> List[EconomicData]:
        """Obtiene datos de inflación del INDEC"""
        indicators = []
        
        try:
            # IPC Nacional - Variación mensual
            url = "https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELNAL_DICI_M_26&limit=2"
            
            async with self.session.get(url, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('data') and len(data['data']) >= 2:
                        latest = data['data'][0]
                        previous = data['data'][1]
                        
                        # Calcular variación mensual
                        current_value = latest[1]
                        prev_value = previous[1]
                        monthly_variation = ((current_value - prev_value) / prev_value) * 100
                        
                        indicators.append(EconomicData(
                            indicator_type='inflacion_mensual',
                            value=monthly_variation,
                            date=datetime.strptime(latest[0], '%Y-%m-%d'),
                            source='INDEC',
                            unit='%',
                            metadata={
                                'ipc_value': current_value,
                                'previous_ipc': prev_value,
                                'series_id': '148.3_INIVELNAL_DICI_M_26'
                            }
                        ))
            
            # EMAE (Estimador Mensual de Actividad Económica)
            url_emae = "https://apis.datos.gob.ar/series/api/series/?ids=143.3_NO_PR_2004_A_21&limit=1"
            
            async with self.session.get(url_emae, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('data') and len(data['data']) > 0:
                        latest = data['data'][0]
                        
                        indicators.append(EconomicData(
                            indicator_type='emae',
                            value=latest[1],
                            date=datetime.strptime(latest[0], '%Y-%m-%d'),
                            source='INDEC',
                            unit='Base 2004=100',
                            metadata={'series_id': '143.3_NO_PR_2004_A_21'}
                        ))
                        
        except Exception as e:
            logger.error(f"Error fetching INDEC data: {e}")
        
        return indicators
    
    async def _fetch_riesgo_pais(self) -> Optional[EconomicData]:
        """Obtiene riesgo país mediante scraping"""
        try:
            # Intentar obtener de Ámbito Financiero
            url = "https://www.ambito.com/contenidos/riesgo-pais.html"
            
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Buscar el valor del riesgo país en el HTML
                    # Esto requiere parsing HTML específico para Ámbito
                    import re
                    pattern = r'riesgo[^>]*>(\d+(?:\.\d+)?)'
                    match = re.search(pattern, html, re.IGNORECASE)
                    
                    if match:
                        value = float(match.group(1))
                        return EconomicData(
                            indicator_type='riesgo_pais',
                            value=value,
                            date=datetime.now(),
                            source='Ámbito Financiero',
                            unit='pb',
                            metadata={'scraping_source': 'ambito.com'}
                        )
            
        except Exception as e:
            logger.error(f"Error scraping riesgo país: {e}")
        
        # Fallback: valor demo pero marcado como tal
        return EconomicData(
            indicator_type='riesgo_pais',
            value=1642.0,
            date=datetime.now(),
            source='Demo/Fallback',
            unit='pb',
            metadata={'is_fallback': True}
        )
    
    async def _fetch_market_indicators(self) -> List[EconomicData]:
        """Obtiene indicadores de mercado (MERVAL, etc.)"""
        indicators = []
        
        try:
            # Intentar obtener MERVAL desde Yahoo Finance API
            symbol = "%5EMERV"  # ^MERV URL encoded
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    chart = data.get('chart', {})
                    result = chart.get('result', [])
                    
                    if result:
                        meta = result[0].get('meta', {})
                        current_price = meta.get('regularMarketPrice')
                        
                        if current_price:
                            indicators.append(EconomicData(
                                indicator_type='merval',
                                value=current_price,
                                date=datetime.now(),
                                source='Yahoo Finance',
                                unit='Points',
                                metadata={
                                    'symbol': '^MERV',
                                    'currency': meta.get('currency', 'ARS')
                                }
                            ))
            
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            
            # Fallback MERVAL
            indicators.append(EconomicData(
                indicator_type='merval',
                value=1456234.0,
                date=datetime.now(),
                source='Demo/Fallback',
                unit='Points',
                metadata={'is_fallback': True}
            ))
        
        return indicators
    
    async def get_historical_data(self, indicator_type: str, days: int = 30) -> List[Dict]:
        """Obtiene datos históricos para un indicador específico"""
        try:
            # Determinar la fuente según el tipo de indicador
            if indicator_type.startswith('dolar_'):
                if indicator_type == 'dolar_blue':
                    return await self.dolar_service.get_historical_blue(days)
                else:
                    # Para otros dólares, usar datos del BCRA si es oficial
                    if indicator_type == 'dolar_oficial':
                        return await self.bcra_service.get_historical_data('usd_oficial', days)
            
            elif indicator_type in ['reservas_bcra', 'tasa_bcra', 'base_monetaria']:
                # Mapear a variables BCRA
                bcra_mapping = {
                    'reservas_bcra': 'reservas',
                    'tasa_bcra': 'tasa_politica',
                    'base_monetaria': 'base_monetaria'
                }
                bcra_key = bcra_mapping.get(indicator_type)
                if bcra_key:
                    return await self.bcra_service.get_historical_data(bcra_key, days)
            
            elif indicator_type == 'inflacion_mensual':
                return await self._get_historical_inflation(days)
            
            # Fallback: generar datos demo históricos
            return self._generate_demo_historical(indicator_type, days)
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {indicator_type}: {e}")
            return []
    
    async def _get_historical_inflation(self, days: int) -> List[Dict]:
        """Obtiene datos históricos de inflación del INDEC"""
        try:
            # Calcular meses a solicitar (aproximado)
            months = max(1, days // 30)
            limit = min(months + 2, 12)  # Máximo 12 meses
            
            url = f"https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELNAL_DICI_M_26&limit={limit}"
            
            async with self.session.get(url, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    historical_data = []
                    if data.get('data'):
                        for i in range(len(data['data']) - 1):
                            current = data['data'][i]
                            previous = data['data'][i + 1]
                            
                            # Calcular variación mensual
                            current_value = current[1]
                            prev_value = previous[1]
                            monthly_variation = ((current_value - prev_value) / prev_value) * 100
                            
                            historical_data.append({
                                'date': current[0],
                                'value': monthly_variation,
                                'source': 'INDEC'
                            })
                    
                    return sorted(historical_data, key=lambda x: x['date'])
                    
        except Exception as e:
            logger.error(f"Error fetching historical inflation: {e}")
        
        return []
    
    def _generate_demo_historical(self, indicator_type: str, days: int) -> List[Dict]:
        """Genera datos históricos demo para indicadores sin fuente real"""
        import random
        
        base_values = {
            'riesgo_pais': 1642.0,
            'merval': 1456234.0,
            'emae': 148.2
        }
        
        base_value = base_values.get(indicator_type, 100.0)
        historical_data = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            # Simulación de variación diaria
            variation = random.uniform(-0.02, 0.02)  # ±2% diario
            value = base_value * (1 + variation * (i / days))
            
            historical_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': value,
                'source': 'Demo'
            })
        
        return historical_data
    
    def _get_fallback_indicators(self) -> List[EconomicData]:
        """Indicadores de fallback cuando fallan las APIs"""
        fallback_data = [
            EconomicData('dolar_oficial', 987.50, datetime.now(), 'Fallback', 'ARS'),
            EconomicData('dolar_blue', 1047.0, datetime.now(), 'Fallback', 'ARS'),
            EconomicData('reservas_bcra', 21500.0, datetime.now(), 'Fallback', 'USD M'),
            EconomicData('riesgo_pais', 1642.0, datetime.now(), 'Fallback', 'pb'),
            EconomicData('tasa_bcra', 118.0, datetime.now(), 'Fallback', '%'),
            EconomicData('inflacion_mensual', 4.2, datetime.now(), 'Fallback', '%'),
            EconomicData('merval', 1456234.0, datetime.now(), 'Fallback', 'Points')
        ]
        return fallback_data
    
    async def refresh_all_data(self) -> Dict[str, Any]:
        """Refresca todos los datos y retorna un resumen"""
        start_time = datetime.now()
        
        try:
            indicators = await self.get_all_current_indicators()
            
            # Estadísticas del refresh
            sources = {}
            for indicator in indicators:
                source = indicator.source
                if source not in sources:
                    sources[source] = 0
                sources[source] += 1
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'total_indicators': len(indicators),
                'sources': sources,
                'duration_seconds': duration,
                'timestamp': datetime.now().isoformat(),
                'real_data_percentage': (sum(1 for i in indicators if 'fallback' not in i.source.lower()) / len(indicators)) * 100 if indicators else 0
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return {
                'success': False,
                'error': str(e),
                'duration_seconds': duration,
                'timestamp': datetime.now().isoformat()
            }

# Test function
async def test_integrated_service():
    """Test completo del servicio integrado"""
    print("🚀 Testing Integrated Data Service...")
    
    async with IntegratedDataService() as service:
        # Test 1: Obtener todos los indicadores
        print("\n📊 Fetching all current indicators...")
        indicators = await service.get_all_current_indicators()
        print(f"Total indicators: {len(indicators)}")
        
        # Agrupar por fuente
        sources = {}
        for indicator in indicators:
            source = indicator.source
            if source not in sources:
                sources[source] = []
            sources[source].append(indicator.indicator_type)
        
        print("\n📈 Indicators by source:")
        for source, types in sources.items():
            print(f"  {source}: {len(types)} indicators")
            for indicator_type in types[:3]:  # Show first 3
                indicator = next(i for i in indicators if i.indicator_type == indicator_type)
                print(f"    - {indicator_type}: {indicator.value} {indicator.unit}")
            if len(types) > 3:
                print(f"    ... and {len(types) - 3} more")
        
        # Test 2: Datos históricos
        print("\n📜 Testing historical data...")
        historical = await service.get_historical_data('dolar_blue', 7)
        print(f"Dólar Blue historical: {len(historical)} points")
        if historical:
            latest = historical[-1]
            print(f"  Latest: ${latest['value']:.2f} on {latest['date']}")
        
        # Test 3: Refresh completo
        print("\n🔄 Testing full refresh...")
        refresh_result = await service.refresh_all_data()
        print(f"Refresh result: {refresh_result}")
        
        print("\n✅ Integrated Service test completed!")

if __name__ == "__main__":
    asyncio.run(test_integrated_service())