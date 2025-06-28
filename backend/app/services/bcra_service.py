# backend/app/services/bcra_service.py
"""
Servicio BCRA unificado – compatible con la lógica actual de los routers.
"""

from __future__ import annotations

import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, List, Optional

from ..config import settings  # sigue funcionando con Pydantic 2

logger = logging.getLogger(__name__)


class BCRAServiceError(Exception):
    """Error específico del servicio BCRA."""


class BCRAService:
    """
    Servicio único de integración con las APIs del BCRA
    Reemplaza todos los módulos duplicados anteriores.
    """

    def __init__(self) -> None:
        self.base_urls = {
            "monetarias": "https://api.bcra.gob.ar/estadisticas/v3.0/Monetarias",
            "cotizaciones": "https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones",
        }
        self.session: Optional[aiohttp.ClientSession] = None

        # Variables esenciales para el MVP / demo
        self.essential_variables: Dict[int, Dict[str, str]] = {
            1: {"key": "reservas_internacionales", "label": "Reservas BCRA", "unit": "USD M"},
            4: {"key": "usd_minorista", "label": "USD Minorista", "unit": "ARS"},
            5: {"key": "usd_mayorista", "label": "USD Mayorista", "unit": "ARS"},
            6: {"key": "tasa_politica", "label": "Tasa Política Monetaria", "unit": "%"},
            27: {"key": "inflacion_mensual", "label": "Inflación Mensual", "unit": "%"},
        }

    # --------------------------------------------------------------------- #
    # Async context-manager helpers
    # --------------------------------------------------------------------- #
    async def __aenter__(self) -> "BCRAService":
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=10),
        )
        return self

    async def __aexit__(self, *_exc) -> None:
        if self.session:
            await self.session.close()

    # --------------------------------------------------------------------- #
    # API públicas usadas por los routers
    # --------------------------------------------------------------------- #
    async def get_current_indicators(self) -> Dict[str, Any]:
        """
        Devuelve todas las variables esenciales + cotizaciones oficiales.
        """
        try:
            if not self.session:
                raise BCRAServiceError("Session not initialized – use `async with`")

            monetary_data = await self._fetch_monetary_variables()
            exchange_data = await self._fetch_exchange_rates()
            return self._consolidate_indicators(monetary_data, exchange_data)

        except Exception as exc:  # noqa: BLE001
            logger.error("Error fetching current indicators: %s", exc)
            return self._get_fallback_data()

    async def get_historical_data(
        self,
        variable_id: int,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Descarga `days` días hacia atrás de una variable monetaria concreta.
        """
        if not self.session:
            raise BCRAServiceError("Session not initialized")

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        url = f"{self.base_urls['monetarias']}/{variable_id}"
        params = {"desde": start_date, "hasta": end_date, "limit": 1000}

        try:
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("results", [])
                logger.warning("BCRA API %s → %s", url, resp.status)
                return []
        except Exception as exc:  # noqa: BLE001
            logger.error("Error fetching historical data %s: %s", variable_id, exc)
            return []

    # --------- Funciones DEMO que esperan los routers (stubs útiles) ------- #
    async def generate_demo_data(self) -> Dict[str, Any]:
        """
        Devuelve datos simulados si el flag DEMO_MODE está activo.
        """
        if settings.DEMO_MODE:
            return self._get_fallback_data()
        return await self.get_current_indicators()

    async def generate_historical_data(self, variable_id: int) -> List[Dict[str, Any]]:
        """
        Envuelve `get_historical_data` con un default de 90 d en modo demo.
        """
        days = 90 if settings.DEMO_MODE else 30
        return await self.get_historical_data(variable_id, days=days)

    async def generate_demo_news(self) -> List[Dict[str, str]]:
        """
        Stub de noticias de demo; completa cuando integres fuente real.
        """
        if not settings.DEMO_MODE:
            return []
        return [
            {
                "title": "Inflación se desacelera por tercer mes consecutivo",
                "source": "Demo News",
                "published_at": datetime.now().isoformat(),
            },
            {
                "title": "Reservas alcanzan máximo de los últimos 12 meses",
                "source": "Demo News",
                "published_at": datetime.now().isoformat(),
            },
        ]

    # --------------------------------------------------------------------- #
    # Helpers internos – fetch + processing
    # --------------------------------------------------------------------- #
    async def _fetch_monetary_variables(self) -> Dict[str, Any]:
        try:
            async with self.session.get(self.base_urls["monetarias"]) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return self._filter_essential_variables(data.get("results", []))
            return {}
        except Exception as exc:  # noqa: BLE001
            logger.error("Error fetching monetary variables: %s", exc)
            return {}

    async def _fetch_exchange_rates(self) -> Dict[str, Any]:
        try:
            async with self.session.get(self.base_urls["cotizaciones"]) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return self._process_exchange_rates(data.get("results", {}))
            return {}
        except Exception as exc:  # noqa: BLE001
            logger.error("Error fetching exchange rates: %s", exc)
            return {}

    # --------------------------- procesamiento ---------------------------- #
    def _filter_essential_variables(self, raw: List[Dict]) -> Dict[str, Any]:
        filtered: Dict[str, Any] = {}
        for item in raw:
            var_id = item.get("idVariable")
            if var_id in self.essential_variables:
                cfg = self.essential_variables[var_id]
                filtered[cfg["key"]] = {
                    "id": var_id,
                    "value": item.get("valor"),
                    "label": cfg["label"],
                    "unit": cfg["unit"],
                    "date": item.get("fecha"),
                    "source": "BCRA",
                }
        return filtered

    def _process_exchange_rates(self, raw: Dict) -> Dict[str, Any]:
        processed: Dict[str, Any] = {}
        for item in raw.get("detalle", []):
            code = item.get("codigoMoneda")
            if code in {"USD", "EUR", "GBP", "BRL"}:
                processed[f"{code.lower()}_official"] = {
                    "value": item.get("tipoCotizacion", 0),
                    "label": f"{code}/ARS Oficial",
                    "unit": "ARS",
                    "date": raw.get("fecha"),
                    "source": "BCRA",
                }
        return processed

    def _consolidate_indicators(
        self,
        monetary: Dict[str, Any],
        exchange: Dict[str, Any],
    ) -> Dict[str, Any]:
        consolidated = {
            "timestamp": datetime.now().isoformat(),
            "source": "BCRA_API",
            "indicators": {**monetary, **exchange},
        }

        # Spread USD minorista vs. mayorista
        if "usd_minorista" in monetary and "usd_mayorista" in monetary:
            spread = (
                monetary["usd_minorista"]["value"]
                - monetary["usd_mayorista"]["value"]
            )
            consolidated["indicators"]["usd_spread"] = {
                "value": spread,
                "label": "Spread USD Oficial",
                "unit": "ARS",
                "source": "CALCULATED",
            }
        return consolidated

    def _get_fallback_data(self) -> Dict[str, Any]:
        return {
            "timestamp": datetime.now().isoformat(),
            "source": "FALLBACK_DATA",
            "indicators": {
                "usd_mayorista": {
                    "value": 1180.0,
                    "label": "USD Mayorista",
                    "unit": "ARS",
                    "source": "DEMO",
                },
                "usd_minorista": {
                    "value": 1190.0,
                    "label": "USD Minorista",
                    "unit": "ARS",
                    "source": "DEMO",
                },
                "reservas_internacionales": {
                    "value": 28_500.0,
                    "label": "Reservas BCRA",
                    "unit": "USD M",
                    "source": "DEMO",
                },
                "tasa_politica": {
                    "value": 40.0,
                    "label": "Tasa Política Monetaria",
                    "unit": "%",
                    "source": "DEMO",
                },
                "inflacion_mensual": {
                    "value": 4.2,
                    "label": "Inflación Mensual",
                    "unit": "%",
                    "source": "DEMO",
                },
            },
        }

    # ------------------- metadatos caché ---------------------------------- #
    @lru_cache(maxsize=128)
    def get_variable_metadata(self, variable_id: int) -> Dict[str, str]:
        return self.essential_variables.get(variable_id, {})


# ------------ Singleton ----------------------------------------------------- #
bcra_service = BCRAService()

# --------- API superficial usada por routers (reexport) -------------------- #
generate_demo_data = bcra_service.generate_demo_data
generate_historical_data = bcra_service.generate_historical_data
generate_demo_news = bcra_service.generate_demo_news
