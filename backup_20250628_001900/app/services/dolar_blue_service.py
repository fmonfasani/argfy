# backend/app/services/dolar_blue_service.py
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class DolarRate:
    """Estructura para cotizaciones del dólar"""
    name: str
    buy: float
    sell: float
    source: str
    timestamp: datetime
    
    def to_dict(self):
        return {
            'name': self.name,
            'buy': self.buy,
            'sell': self.sell,
            'source': self.source,
            'timestamp': self.timestamp.isoformat()
        }

class DolarBlueService:
    """Servicio para obtener cotizaciones del dólar blue de múltiples fuentes"""
    
    def __init__(self):
        self.session = None
        self._cache = {}
        self._cache_ttl = 120  # 2 minutos para dólar blue
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_all_rates(self) -> Dict[str, DolarRate]:
        """Obtiene todas las cotizaciones disponibles de múltiples fuentes"""
        rates = {}
        
        # Ejecutar todas las fuentes en paralelo
        tasks = [
            self._fetch_bluelytics(),
            self._fetch_dolarapi(),
            self._fetch_dolarsi(),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, dict):
                rates.update(result)
            elif isinstance(result, Exception):
                logger.error(f"Error fetching dollar rates: {result}")
        
        return rates
    
    async def get_blue_rate(self) -> Optional[DolarRate]:
        """Obtiene la cotización del dólar blue (mejor fuente disponible)"""
        cache_key = "dolar_blue_rate"
        
        # Check cache
        if cache_key in self._cache:
            cache_time, cache_data = self._cache[cache_key]
            if (datetime.now() - cache_time).total_seconds() < self._cache_ttl:
                return cache_data
        
        # Try multiple sources in order of preference
        sources = [
            self._fetch_bluelytics,
            self._fetch_dolarapi,
            self._fetch_dolarsi
        ]
        
        for source_func in sources:
            try:
                rates = await source_func()
                if 'blue' in rates:
                    blue_rate = rates['blue']
                    # Cache the result
                    self._cache[cache_key] = (datetime.now(), blue_rate)
                    return blue_rate
            except Exception as e:
                logger.error(f"Error in source {source_func.__name__}: {e}")
                continue
        
        logger.error("All dollar blue sources failed")
        return None
    
    async def _fetch_bluelytics(self) -> Dict[str, DolarRate]:
        """Fetch from Bluelytics API (preferred source)"""
        try:
            url = "https://api.bluelytics.com.ar/v2/latest"
            
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    rates = {}
                    timestamp = datetime.now()
                    
                    # Dólar Blue
                    if 'blue' in data:
                        blue_data = data['blue']
                        rates['blue'] = DolarRate(
                            name='Dólar Blue',
                            buy=float(blue_data.get('value_buy', 0)),
                            sell=float(blue_data.get('value_sell', 0)),
                            source='Bluelytics',
                            timestamp=timestamp
                        )
                    
                    # Dólar Oficial
                    if 'oficial' in data:
                        oficial_data = data['oficial']
                        rates['oficial'] = DolarRate(
                            name='Dólar Oficial',
                            buy=float(oficial_data.get('value_buy', 0)),
                            sell=float(oficial_data.get('value_sell', 0)),
                            source='Bluelytics',
                            timestamp=timestamp
                        )
                    
                    # Dólar MEP (if available)
                    if 'blue_gap' in data:
                        # Calcular MEP aproximado
                        blue_rate = rates.get('blue')
                        oficial_rate = rates.get('oficial')
                        
                        if blue_rate and oficial_rate:
                            gap = float(data.get('blue_gap', 0))
                            mep_rate = oficial_rate.sell * (1 + gap / 100 * 0.7)  # MEP suele estar entre oficial y blue
                            
                            rates['mep'] = DolarRate(
                                name='Dólar MEP',
                                buy=mep_rate * 0.995,
                                sell=mep_rate,
                                source='Bluelytics (calculated)',
                                timestamp=timestamp
                            )
                    
                    logger.info(f"Bluelytics: fetched {len(rates)} rates")
                    return rates
                else:
                    logger.error(f"Bluelytics API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error fetching Bluelytics: {e}")
            
        return {}
    
    async def _fetch_dolarapi(self) -> Dict[str, DolarRate]:
        """Fetch from DolarAPI"""
        try:
            url = "https://dolarapi.com/v1/dolares"
            
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    rates = {}
                    timestamp = datetime.now()
                    
                    # Map DolarAPI names to our format
                    name_mapping = {
                        'Blue': 'blue',
                        'Oficial': 'oficial',
                        'MEP': 'mep',
                        'CCL': 'ccl',
                        'Tarjeta': 'tarjeta',
                        'Mayorista': 'mayorista'
                    }
                    
                    for item in data:
                        api_name = item.get('nombre', '')
                        our_key = name_mapping.get(api_name)
                        
                        if our_key and item.get('compra') and item.get('venta'):
                            rates[our_key] = DolarRate(
                                name=f'Dólar {api_name}',
                                buy=float(item['compra']),
                                sell=float(item['venta']),
                                source='DolarAPI',
                                timestamp=timestamp
                            )
                    
                    logger.info(f"DolarAPI: fetched {len(rates)} rates")
                    return rates
                else:
                    logger.error(f"DolarAPI error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error fetching DolarAPI: {e}")
            
        return {}
    
    async def _fetch_dolarsi(self) -> Dict[str, DolarRate]:
        """Fetch from DolarSi (backup source)"""
        try:
            url = "https://www.dolarsi.com/api/api.php?type=valoresprincipales"
            
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    rates = {}
                    timestamp = datetime.now()
                    
                    # Parse DolarSi format
                    for item in data:
                        casa = item.get('casa', {})
                        nombre = casa.get('nombre', '').lower()
                        
                        # Map DolarSi names
                        key = None
                        display_name = None
                        
                        if 'blue' in nombre:
                            key = 'blue'
                            display_name = 'Dólar Blue'
                        elif 'oficial' in nombre:
                            key = 'oficial'
                            display_name = 'Dólar Oficial'
                        elif 'mep' in nombre or 'bolsa' in nombre:
                            key = 'mep'
                            display_name = 'Dólar MEP'
                        elif 'ccl' in nombre or 'contado con liqui' in nombre:
                            key = 'ccl'
                            display_name = 'Dólar CCL'
                        
                        if key and casa.get('compra') and casa.get('venta'):
                            try:
                                # Clean price strings (remove $ and ,)
                                compra = casa['compra'].replace('$', '').replace(',', '.')
                                venta = casa['venta'].replace('$', '').replace(',', '.')
                                
                                rates[key] = DolarRate(
                                    name=display_name,
                                    buy=float(compra),
                                    sell=float(venta),
                                    source='DolarSi',
                                    timestamp=timestamp
                                )
                            except (ValueError, TypeError) as e:
                                logger.error(f"Error parsing DolarSi prices for {nombre}: {e}")
                                continue
                    
                    logger.info(f"DolarSi: fetched {len(rates)} rates")
                    return rates
                else:
                    logger.error(f"DolarSi error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error fetching DolarSi: {e}")
            
        return {}
    
    async def get_historical_blue(self, days: int = 30) -> List[Dict]:
        """Intenta obtener datos históricos del dólar blue"""
        try:
            # Bluelytics tiene endpoint de evolución
            url = f"https://api.bluelytics.com.ar/v2/evolution.json"
            
            async with self.session.get(url, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Filtrar últimos N días
                    cutoff_date = datetime.now() - timedelta(days=days)
                    historical_data = []
                    
                    for item in data:
                        date_str = item.get('date')
                        if date_str:
                            try:
                                item_date = datetime.strptime(date_str, '%Y-%m-%d')
                                if item_date >= cutoff_date:
                                    blue_data = item.get('blue', {})
                                    if blue_data.get('value_sell'):
                                        historical_data.append({
                                            'date': date_str,
                                            'value': float(blue_data['value_sell']),
                                            'buy': float(blue_data.get('value_buy', 0)),
                                            'sell': float(blue_data.get('value_sell', 0)),
                                            'source': 'Bluelytics'
                                        })
                            except (ValueError, TypeError):
                                continue
                    
                    return sorted(historical_data, key=lambda x: x['date'])
                else:
                    logger.error(f"Bluelytics evolution API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error fetching historical blue: {e}")
        
        return []
    
    def get_rates_summary(self, rates: Dict[str, DolarRate]) -> Dict[str, Any]:
        """Genera un resumen de las cotizaciones"""
        if not rates:
            return {}
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_rates': len(rates),
            'sources': list(set(rate.source for rate in rates.values())),
            'rates': {}
        }
        
        for key, rate in rates.items():
            summary['rates'][key] = {
                'name': rate.name,
                'buy': rate.buy,
                'sell': rate.sell,
                'spread': round(rate.sell - rate.buy, 2),
                'spread_pct': round((rate.sell - rate.buy) / rate.buy * 100, 2) if rate.buy > 0 else 0,
                'source': rate.source
            }
        
        # Calcular brecha si tenemos oficial y blue
        if 'oficial' in rates and 'blue' in rates:
            oficial_sell = rates['oficial'].sell
            blue_sell = rates['blue'].sell
            
            if oficial_sell > 0:
                gap = ((blue_sell - oficial_sell) / oficial_sell) * 100
                summary['blue_gap'] = round(gap, 1)
        
        return summary

# Función de conveniencia para testing
async def test_dolar_blue_service():
    """Test function for the dollar blue service"""
    async with DolarBlueService() as service:
        print("🔄 Testing Dólar Blue Service...")
        
        # Test 1: Get all rates
        print("\n💰 Fetching all dollar rates...")
        all_rates = await service.get_all_rates()
        print(f"Found {len(all_rates)} different rates")
        
        for key, rate in all_rates.items():
            print(f"  {rate.name}: ${rate.buy:.2f} / ${rate.sell:.2f} ({rate.source})")
        
        # Test 2: Get blue specifically
        print("\n💵 Fetching blue rate specifically...")
        blue_rate = await service.get_blue_rate()
        if blue_rate:
            print(f"Blue: ${blue_rate.buy:.2f} / ${blue_rate.sell:.2f}")
        else:
            print("❌ Could not fetch blue rate")
        
        # Test 3: Historical data
        print("\n📊 Fetching historical blue data...")
        historical = await service.get_historical_blue(7)
        print(f"Historical data points: {len(historical)}")
        
        if historical:
            latest = historical[-1]
            oldest = historical[0]
            print(f"  Range: {oldest['date']} to {latest['date']}")
            print(f"  Latest: ${latest['value']}")
        
        # Test 4: Summary
        print("\n📋 Rates summary...")
        summary = service.get_rates_summary(all_rates)
        if 'blue_gap' in summary:
            print(f"  Blue gap vs official: {summary['blue_gap']}%")
        
        print("\n✅ Dólar Blue Service test completed!")

if __name__ == "__main__":
    asyncio.run(test_dolar_blue_service())