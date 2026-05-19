"""
Pydantic schemas para /api/v1/fundamentals.
Espejan los Zod schemas en frontend/src/lib/types.ts.
Si se actualiza uno, actualizar el otro.
"""
from typing import Optional, Any
from pydantic import BaseModel, Field


class RatioSnapshot(BaseModel):
    byma_ticker:              str
    ticker_sec:               Optional[str] = None
    cik:                      Optional[str] = None
    period_end:               Optional[str] = None
    as_of:                    Optional[str] = None
    precio_usd:               Optional[float] = None
    currency:                 Optional[str] = None
    exchange:                 Optional[str] = None
    nombre:                   Optional[str] = None
    country:                  Optional[str] = None
    year_high:                Optional[float] = None
    year_low:                 Optional[float] = None
    dif_max_52w:              Optional[float] = None
    dif_min_52w:              Optional[float] = None
    per_ttm:                  Optional[float] = None
    eps_ttm_diluted:          Optional[float] = None
    margen_neto_ttm:          Optional[float] = None
    roe_cagr_5y:              Optional[float] = None
    deuda_lp_sobre_ebitda:    Optional[float] = None
    deuda_total_sobre_ebitda: Optional[float] = None
    fcfonce_equity_lp:        Optional[float] = None
    fcfonce_neto_caja:        Optional[float] = None
    payout_ttm:               Optional[float] = None


class SortInfo(BaseModel):
    by:   str
    desc: bool


class ScreenerResponse(BaseModel):
    count:   int
    total:   int
    offset:  int
    limit:   int
    filters: dict[str, Any]
    sort:    SortInfo
    data:    list[RatioSnapshot]


class CoverageItem(BaseModel):
    con_dato: int
    pct:      float


class CoverageResponse(BaseModel):
    total:    int
    coverage: dict[str, CoverageItem]


class CompanyInfo(BaseModel):
    nombre:      Optional[str] = None
    ticker_sec:  Optional[str] = None
    cik:         Optional[str] = None
    exchange:    Optional[str] = None
    country:     Optional[str] = None
    sector:      Optional[str] = None
    industry:    Optional[str] = None
    has_sec:     Optional[bool] = None
    source_tier: Optional[int] = None


class TickerDetail(BaseModel):
    ratios:  RatioSnapshot
    company: CompanyInfo
