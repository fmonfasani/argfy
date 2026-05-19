"""
Router de fundamentals — CEDEARs + BYMA locales con ratios desde SEC EDGAR.

Endpoints:
- GET /api/v1/fundamentals/screener       listado filtrable (PER, ROE, etc.)
- GET /api/v1/fundamentals/coverage       meta: cuántas empresas con cada ratio
- GET /api/v1/fundamentals/{byma_ticker}  detalle del último snapshot
- GET /api/v1/fundamentals/{byma_ticker}/price     histórico de precios diarios
- GET /api/v1/fundamentals/{byma_ticker}/history   serie temporal de una métrica
"""
from datetime import timedelta, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import Company, RatioQuarterly, PriceDaily
from ..middleware.feature_gate import require_feature
from ..schemas.fundamentals import (
    ScreenerResponse,
    CoverageResponse,
    TickerDetail,
)

router = APIRouter(prefix="/api/v1/fundamentals", tags=["fundamentals"])


def _ratio_to_dict(r: RatioQuarterly):
    return {
        "byma_ticker":              r.byma_ticker,
        "ticker_sec":               r.ticker_sec,
        "cik":                      r.cik,
        "period_end":               r.period_end.isoformat() if r.period_end else None,
        "as_of":                    r.as_of.isoformat() if r.as_of else None,
        "precio_usd":               r.precio_usd,
        "currency":                 r.currency,
        "exchange":                 r.exchange,
        "year_high":                r.year_high,
        "year_low":                 r.year_low,
        "dif_max_52w":              r.dif_max_52w,
        "dif_min_52w":              r.dif_min_52w,
        "per_ttm":                  r.per_ttm,
        "eps_ttm_diluted":          r.eps_ttm_diluted,
        "margen_neto_ttm":          r.margen_neto_ttm,
        "roe_cagr_5y":              r.roe_cagr_5y,
        "deuda_lp_sobre_ebitda":    r.deuda_lp_sobre_ebitda,
        "deuda_total_sobre_ebitda": r.deuda_total_sobre_ebitda,
        "fcfonce_equity_lp":        r.fcfonce_equity_lp,
        "fcfonce_neto_caja":        r.fcfonce_neto_caja,
        "payout_ttm":               r.payout_ttm,
    }


# Columnas válidas para sort en /screener
SORTABLE_COLUMNS = {
    "byma_ticker", "ticker_sec", "exchange", "precio_usd",
    "year_high", "year_low",
    "per_ttm", "eps_ttm_diluted", "margen_neto_ttm", "roe_cagr_5y",
    "deuda_lp_sobre_ebitda", "deuda_total_sobre_ebitda",
    "fcfonce_equity_lp", "fcfonce_neto_caja", "payout_ttm", "cagr_eps_5y",
}

# Métricas válidas para /history
METRIC_COLUMNS = {
    "per_ttm", "eps_ttm_diluted", "margen_neto_ttm", "roe_cagr_5y",
    "deuda_lp_sobre_ebitda", "deuda_total_sobre_ebitda",
    "fcfonce_equity_lp", "fcfonce_neto_caja", "payout_ttm", "cagr_eps_5y",
    "revenue_ttm", "netincome_ttm", "ebitda_ttm", "fcf_ttm",
}


def _last_period_subquery(db: Session):
    """Subquery: último period_end por byma_ticker."""
    return (
        db.query(
            RatioQuarterly.byma_ticker,
            func.max(RatioQuarterly.period_end).label("max_period"),
        )
        .group_by(RatioQuarterly.byma_ticker)
        .subquery()
    )


@router.get("/screener", response_model=ScreenerResponse)
def screener(
    per_max:    Optional[float] = Query(None, description="PER TTM máximo"),
    per_min:    Optional[float] = Query(None, description="PER TTM mínimo"),
    roe_min:    Optional[float] = Query(None, description="ROE CAGR 5y mínimo (ej. 0.15)"),
    margen_min: Optional[float] = Query(None, description="Margen Neto mínimo (ej. 0.10)"),
    deuda_max:  Optional[float] = Query(None, description="Deuda Total / EBITDA máximo"),
    payout_max: Optional[float] = Query(None, description="Payout TTM máximo (ej. 0.80)"),
    exchange:   Optional[str]   = Query(None, description="NYSE, NMS, NASDAQ, BYMA, ..."),
    country:    Optional[str]   = Query(None, description="US, AR, OTROS"),
    q:          Optional[str]   = Query(None, description="Búsqueda por ticker o nombre"),
    sort_by:    str             = Query("per_ttm", description="Campo para ordenar"),
    sort_desc:  bool            = Query(False),
    offset:     int             = Query(0, ge=0, description="Paginación: offset"),
    limit:      int             = Query(100, ge=1, le=1000, description="Paginación: limit"),
    db: Session = Depends(get_db),
):
    """Screener filtrable. Devuelve el último snapshot por byma_ticker.
    Soporta paginación server-side con offset/limit y búsqueda por q."""
    last_sub = _last_period_subquery(db)

    qry = (
        db.query(RatioQuarterly, Company.nombre, Company.country)
        .join(Company, RatioQuarterly.byma_ticker == Company.byma_ticker)
        .join(last_sub, and_(
            RatioQuarterly.byma_ticker == last_sub.c.byma_ticker,
            RatioQuarterly.period_end  == last_sub.c.max_period,
        ))
    )

    if per_max    is not None: qry = qry.filter(RatioQuarterly.per_ttm <= per_max,    RatioQuarterly.per_ttm.isnot(None))
    if per_min    is not None: qry = qry.filter(RatioQuarterly.per_ttm >= per_min,    RatioQuarterly.per_ttm.isnot(None))
    if roe_min    is not None: qry = qry.filter(RatioQuarterly.roe_cagr_5y >= roe_min, RatioQuarterly.roe_cagr_5y.isnot(None))
    if margen_min is not None: qry = qry.filter(RatioQuarterly.margen_neto_ttm >= margen_min, RatioQuarterly.margen_neto_ttm.isnot(None))
    if deuda_max  is not None: qry = qry.filter(RatioQuarterly.deuda_total_sobre_ebitda <= deuda_max, RatioQuarterly.deuda_total_sobre_ebitda.isnot(None))
    if payout_max is not None: qry = qry.filter(RatioQuarterly.payout_ttm <= payout_max, RatioQuarterly.payout_ttm.isnot(None))
    if exchange:               qry = qry.filter(RatioQuarterly.exchange == exchange.upper())
    if country:
        if country == "OTROS":
            qry = qry.filter(Company.country.notin_(["US", "AR"]))
        else:
            qry = qry.filter(Company.country == country.upper())
    if q:
        like = f"%{q}%"
        qry = qry.filter(
            or_(
                Company.byma_ticker.ilike(like),
                Company.nombre.ilike(like),
            )
        )

    if sort_by in SORTABLE_COLUMNS:
        col = getattr(RatioQuarterly, sort_by)
        qry = qry.order_by(col.desc() if sort_desc else col.asc())

    total = qry.count()
    rows = qry.offset(offset).limit(limit).all()

    data = []
    for r, nombre, ctry in rows:
        d = _ratio_to_dict(r)
        d["nombre"] = nombre
        d["country"] = ctry
        data.append(d)

    return {
        "count":   len(data),
        "total":   total,
        "offset":  offset,
        "limit":   limit,
        "filters": {
            "per_max": per_max, "per_min": per_min, "roe_min": roe_min,
            "margen_min": margen_min, "deuda_max": deuda_max,
            "payout_max": payout_max, "exchange": exchange,
            "country": country, "q": q,
        },
        "sort": {"by": sort_by, "desc": sort_desc},
        "data": data,
    }


@router.get("/coverage", response_model=CoverageResponse)
def coverage(db: Session = Depends(get_db)):
    """Stats: cuántos tickers tienen cada ratio en el último snapshot.
    Una sola query con conditional aggregates en vez de N+1."""
    sub = _last_period_subquery(db)
    campos = [
        "per_ttm", "eps_ttm_diluted", "margen_neto_ttm", "roe_cagr_5y",
        "deuda_lp_sobre_ebitda", "deuda_total_sobre_ebitda",
        "fcfonce_equity_lp", "fcfonce_neto_caja", "payout_ttm",
    ]

    columns = [func.count().label("total")]
    for c in campos:
        col = getattr(RatioQuarterly, c)
        columns.append(
            func.sum(case((col.isnot(None), 1), else_=0)).label(c)
        )

    row = (
        db.query(*columns)
        .select_from(RatioQuarterly)
        .join(sub, and_(
            RatioQuarterly.byma_ticker == sub.c.byma_ticker,
            RatioQuarterly.period_end  == sub.c.max_period,
        ))
        .one()
    )

    total = int(row.total or 0)
    if total == 0:
        return {"total": 0, "coverage": {}}

    cov = {}
    for c in campos:
        n = int(getattr(row, c) or 0)
        cov[c] = {"con_dato": n, "pct": round(n / total * 100, 1)}

    return {"total": total, "coverage": cov}


@router.get("/{byma_ticker}/price",
    dependencies=[Depends(require_feature("historical_prices"))])
def price_history(
    byma_ticker: str,
    period:   str = Query("5y", pattern=r"^(1m|6m|1y|5y|max)$"),
    interval: str = Query("1d", pattern=r"^(1d|1w|1mo)$"),
    db: Session = Depends(get_db),
):
    """Precios históricos diarios desde prices_daily."""
    days_map = {"1m": 30, "6m": 180, "1y": 365, "5y": 1825}
    today = date.today()
    since = (
        date(2021, 1, 1)
        if period in ("max", "5y")
        else today - timedelta(days=days_map[period])
    )
    rows = (
        db.query(PriceDaily)
        .filter(PriceDaily.byma_ticker == byma_ticker.upper(), PriceDaily.date >= since)
        .order_by(PriceDaily.date.asc())
        .all()
    )
    if not rows:
        raise HTTPException(404, detail=f"No price data for '{byma_ticker}'")

    return {
        "byma_ticker": byma_ticker.upper(),
        "period": period,
        "interval": interval,
        "count": len(rows),
        "data": [
            {
                "date": r.date.isoformat(),
                "open": r.open, "high": r.high, "low": r.low,
                "close": r.close, "adj_close": r.adj_close,
                "volume": r.volume,
            }
            for r in rows
        ],
    }


@router.get("/{byma_ticker}/history",
    dependencies=[Depends(require_feature("metric_history"))])
def metric_history(
    byma_ticker: str,
    metric:   str = Query("per_ttm", description="Métrica a graficar"),
    from_date: Optional[str] = Query(None, alias="from", description="YYYY-MM-DD"),
    to_date:   Optional[str] = Query(None, alias="to", description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    """Serie temporal de una métrica fundamental desde ratios_quarterly."""
    if metric not in METRIC_COLUMNS:
        valid = ", ".join(sorted(METRIC_COLUMNS))
        raise HTTPException(400, detail=f"Metric inválida. Válidas: {valid}")

    qry = (
        db.query(RatioQuarterly)
        .filter(RatioQuarterly.byma_ticker == byma_ticker.upper())
    )
    if from_date:
        qry = qry.filter(RatioQuarterly.period_end >= date.fromisoformat(from_date))
    if to_date:
        qry = qry.filter(RatioQuarterly.period_end <= date.fromisoformat(to_date))

    rows = qry.order_by(RatioQuarterly.period_end.asc()).all()
    if not rows:
        raise HTTPException(404, detail=f"No history for '{byma_ticker}' / metric '{metric}'")

    return {
        "byma_ticker": byma_ticker.upper(),
        "metric": metric,
        "count": len(rows),
        "data": [
            {"period_end": r.period_end.isoformat(), "value": getattr(r, metric)}
            for r in rows
        ],
    }


@router.get("/{byma_ticker}", response_model=TickerDetail)
def detalle(byma_ticker: str, db: Session = Depends(get_db)):
    """Detalle de un BYMA ticker (último snapshot)."""
    r = (
        db.query(RatioQuarterly)
        .filter(RatioQuarterly.byma_ticker == byma_ticker.upper())
        .order_by(RatioQuarterly.period_end.desc())
        .first()
    )
    if not r:
        raise HTTPException(status_code=404, detail=f"Ticker '{byma_ticker}' no encontrado")

    c = db.query(Company).filter(Company.byma_ticker == byma_ticker.upper()).first()

    return {
        "ratios":  _ratio_to_dict(r),
        "company": {
            "nombre":      c.nombre   if c else None,
            "ticker_sec":  c.ticker_sec if c else r.ticker_sec,
            "cik":         c.cik       if c else r.cik,
            "exchange":    c.exchange  if c else r.exchange,
            "country":     c.country   if c else None,
            "sector":      c.sector    if c else None,
            "industry":    c.industry  if c else None,
            "has_sec":     c.has_sec   if c else None,
            "source_tier": c.source_tier if c else None,
        },
    }
