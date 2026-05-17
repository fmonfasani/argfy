"""
Tests del motor de ratios: PER, ROE5y, Margen, Deuda/EBITDA.
Verifica que los cálculos desde datos conocidos sean correctos.
"""
from decimal import Decimal, ROUND_HALF_UP


def test_per_ttm_logic(seed_ratios):
    """PER = precio / EPS. AAPL: 175 / 6.2 ≈ 28.23"""
    from app.models import RatioQuarterly
    r = next(r for r in seed_ratios if r.byma_ticker == "AAPL")
    expected = round(175.0 / 6.2, 2)
    assert abs(r.per_ttm - expected) < 0.1, f"PER {r.per_ttm} != ~{expected}"


def test_margen_neto_logic(seed_ratios):
    """Margen Neto TTM = NetIncome / Revenue."""
    r = next(r for r in seed_ratios if r.byma_ticker == "AAPL")
    expected = round(95000 / 395000, 4)
    assert abs(r.margen_neto_ttm - expected) < 0.01, f"Margen {r.margen_neto_ttm} != ~{expected}"


def test_deuda_ebitda_logic(seed_ratios):
    """Deuda Total / EBITDA: debe ser un ratio >= 0."""
    r = next(r for r in seed_ratios if r.byma_ticker == "GGAL")
    assert r.deuda_total_sobre_ebitda > 0
    assert r.deuda_total_sobre_ebitda < 10


def test_payout_ttm(seed_ratios):
    """Payout = Dividendos / NetIncome. MELI paga 0."""
    r = next(r for r in seed_ratios if r.byma_ticker == "MELI")
    assert r.payout_ttm == 0.0


def test_all_tickers_have_latest_period(seed_ratios):
    """Cada ticker debe tener su period_end correcto."""
    for r in seed_ratios:
        assert r.period_end is not None
        assert str(r.period_end) == "2025-12-31"


def test_precio_usd_not_null(seed_ratios):
    """Todos los precios deben ser > 0."""
    for r in seed_ratios:
        assert r.precio_usd is not None
        assert r.precio_usd > 0
