"""
ETL: carga valuarty/data_export/ → Postgres argfy.

Entrada (estructura real entregada por 08_generar_dataset_etl.py):
    data_export/
    ├── manifest.json
    ├── company_master.csv              (581 filas)
    ├── ratio_snapshots.csv             (415 filas — último snapshot calculado)
    ├── quarterly_fundamentals.csv      (318k filas — XBRL long-format)
    ├── daily_prices/{ticker_sec}.csv   (295 archivos)
    └── byma_locales/{byma_ticker}.csv  (79 archivos)

Salida → tablas:
    companies            (1 fila por byma_ticker, ~581)
    prices_daily         (1 fila por (byma_ticker, date), ~580k con duplicación cross-byma)
    fundamentals_raw     (1 fila por cik, JSONB de métricas, ~291)
    ratios_quarterly     (1 fila por (byma_ticker, period_end=manifest.generated_at), 415)

Uso:
    cd argfy/backend
    DATABASE_URL=postgresql+psycopg2://argfy:argfy_dev@localhost:5544/argfy \\
        python scripts/load_data_export.py

Override path: VALUARTY_DIR=/ruta python scripts/load_data_export.py
Idempotente: TRUNCATE de las 4 tablas antes de cargar.
"""
import json
import os
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import pandas as pd
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]   # argfy/backend/
sys.path.insert(0, str(ROOT))

from app.database import engine, SessionLocal, IS_SQLITE  # noqa: E402
from app.models import (                                  # noqa: E402
    Company, PriceDaily, FundamentalRaw, RatioQuarterly,
)

VALUARTY_DIR = Path(os.getenv("VALUARTY_DIR", ROOT.parent.parent))
EXPORT_DIR   = VALUARTY_DIR / "data_export"


def pad_cik(v) -> str | None:
    """SEC CIK como string de 10 dígitos con padding ('0000320193')."""
    if v is None or pd.isna(v):
        return None
    try:
        return str(int(v)).zfill(10)
    except (ValueError, TypeError):
        s = str(v).strip()
        return s.zfill(10) if s.isdigit() else s


def load_companies(db, cm_csv: Path) -> dict[str, list[str]]:
    """
    Carga companies. Devuelve mapping ticker_sec -> [byma_tickers]
    (varios byma_tickers pueden compartir ticker_sec; ej. AAPL + AAPLD).
    """
    df = pd.read_csv(cm_csv, dtype={"ticker_sec": "string", "byma_ticker": "string"})
    print(f"  company_master.csv : {len(df)} filas")

    sec_to_bymas: dict[str, list[str]] = defaultdict(list)
    objs = []
    for r in df.itertuples(index=False):
        byma = r.byma_ticker
        if not byma or pd.isna(byma):
            continue
        ticker_sec = r.ticker_sec if not pd.isna(r.ticker_sec) else None
        cik        = pad_cik(r.cik)
        exch       = None if pd.isna(r.exchange) else str(r.exchange)
        es_local   = bool(r.es_local_byma)
        es_cedear  = bool(r.es_cedear)
        has_fin    = bool(r.has_financials)

        country  = "AR" if es_local else ("US" if cik else None)
        currency = "ARS" if es_local else ("USD" if es_cedear else None)
        tier     = 1 if has_fin else (4 if es_local else 3)

        objs.append(Company(
            byma_ticker = byma,
            ticker_sec  = ticker_sec,
            cik         = cik,
            nombre      = None if pd.isna(r.nombre) else r.nombre,
            exchange    = exch,
            country     = country,
            currency    = currency,
            source_tier = tier,
            has_sec     = has_fin,
            has_yf      = True,    # asumimos que todos tienen precio (ver fase 2)
            has_fmp     = False,
        ))
        if ticker_sec:
            sec_to_bymas[ticker_sec].append(byma)

    db.bulk_save_objects(objs)
    db.commit()
    print(f"  companies inserted : {len(objs)}")
    return sec_to_bymas


def _load_price_dir(db, dirpath: Path, ticker_col: str, lookup_fn) -> int:
    """
    Lee todos los CSVs de dirpath, mapea cada fila al/los byma_ticker(s) destino
    via lookup_fn(ticker_from_file) -> list[byma_ticker], y bulk-inserta.
    """
    total = 0
    files = sorted(dirpath.glob("*.csv"))
    print(f"  {dirpath.name}: {len(files)} archivos")
    for i, fp in enumerate(files):
        df = pd.read_csv(fp)
        if df.empty:
            continue
        # ticker viene en columna 'ticker' (daily_prices) o 'ticker_byma' (byma_locales)
        ticker_from_file = df[ticker_col].iloc[0]
        bymas = lookup_fn(ticker_from_file)
        if not bymas:
            continue

        # convertir a list[dict] mínimo
        df = df.rename(columns={"adj_close": "adj_close"})  # noop, claridad
        df["date"] = pd.to_datetime(df["date"]).dt.date
        base_rows = df[["date","open","high","low","close","adj_close","volume"]].to_dict("records")

        is_local = (ticker_col == "ticker_byma")
        currency = "ARS" if is_local else "USD"
        source   = "yfinance"

        rows_out = []
        for byma in bymas:
            for r in base_rows:
                rows_out.append({
                    "byma_ticker": byma,
                    "date":        r["date"],
                    "open":        r["open"],
                    "high":        r["high"],
                    "low":         r["low"],
                    "close":       r["close"],
                    "adj_close":   r["adj_close"],
                    "volume":      int(r["volume"]) if pd.notna(r["volume"]) else None,
                    "currency":    currency,
                    "source":      source,
                })
        if rows_out:
            db.execute(PriceDaily.__table__.insert(), rows_out)
            total += len(rows_out)

        if (i + 1) % 50 == 0:
            db.commit()
            print(f"    .. {i+1}/{len(files)} archivos, {total} filas hasta ahora")
    db.commit()
    return total


def load_prices(db, sec_to_bymas: dict[str, list[str]]):
    # daily_prices/{ticker_sec}.csv → fanout a múltiples byma_tickers
    n_us = _load_price_dir(
        db,
        EXPORT_DIR / "daily_prices",
        ticker_col="ticker",
        lookup_fn=lambda t: sec_to_bymas.get(str(t), []),
    )
    # byma_locales/{byma_ticker}.csv → 1:1
    valid_bymas = {b for lst in sec_to_bymas.values() for b in lst}
    # también incluir bymas locales (no están en sec_to_bymas porque no tienen ticker_sec)
    bymas_in_db = set(r[0] for r in db.execute(text("SELECT byma_ticker FROM companies")).all())
    valid_bymas |= bymas_in_db

    n_local = _load_price_dir(
        db,
        EXPORT_DIR / "byma_locales",
        ticker_col="ticker_byma",
        lookup_fn=lambda t: [str(t)] if str(t) in valid_bymas else [],
    )
    print(f"  prices_daily inserted: {n_us} (US) + {n_local} (BYMA) = {n_us + n_local}")


def load_fundamentals_raw(db, qf_csv: Path):
    """
    Lee quarterly_fundamentals.csv (long-format) y la rearma a JSONB:
        {metrica: {"unit": str, "datos": [{start, end, val, fy, fp, form, filed, frame}, ...]}}
    Una fila por cik.
    """
    print(f"  leyendo quarterly_fundamentals.csv (puede tardar)...")
    df = pd.read_csv(qf_csv, dtype={"cik": "Int64", "ticker_sec": "string"})
    df["cik_padded"] = df["cik"].apply(pad_cik)
    print(f"  datapoints crudos  : {len(df):,}")
    print(f"  CIKs distintos     : {df['cik_padded'].nunique()}")

    inserted = 0
    for cik, g in df.groupby("cik_padded"):
        if not cik:
            continue
        ticker_sec = g["ticker_sec"].dropna().iloc[0] if g["ticker_sec"].notna().any() else None

        metrics: dict = {}
        for metrica, g2 in g.groupby("metrica"):
            unit = g2["unit"].dropna().iloc[0] if g2["unit"].notna().any() else None
            datos = []
            for r in g2.itertuples(index=False):
                datos.append({
                    "start":  None if pd.isna(r.start) else r.start,
                    "end":    None if pd.isna(r.end)   else r.end,
                    "val":    None if pd.isna(r.val)   else float(r.val),
                    "fy":     None if pd.isna(r.fy)    else int(r.fy),
                    "fp":     None if pd.isna(r.fp)    else r.fp,
                    "form":   None if pd.isna(r.form)  else r.form,
                    "filed":  None if pd.isna(r.filed) else r.filed,
                    "frame":  None if pd.isna(r.frame) else r.frame,
                })
            metrics[metrica] = {"unit": unit, "datos": datos}

        db.add(FundamentalRaw(
            cik        = cik,
            ticker_sec = ticker_sec,
            source     = "sec",
            currency   = "USD",
            metrics    = metrics,
        ))
        inserted += 1
        if inserted % 50 == 0:
            db.commit()
            print(f"    .. {inserted} CIKs commiteados")
    db.commit()
    print(f"  fundamentals_raw inserted: {inserted}")


def load_ratios_snapshot(db, rs_csv: Path, as_of_date: date):
    df = pd.read_csv(rs_csv)
    df["cik_padded"] = df["cik"].apply(pad_cik)
    print(f"  ratio_snapshots.csv: {len(df)} filas (period_end={as_of_date})")

    rows = []
    for r in df.itertuples(index=False):
        rows.append({
            "byma_ticker":              r.byma_ticker,
            "period_end":               as_of_date,
            "as_of":                    None,
            "ticker_sec":               None if pd.isna(r.ticker_sec) else r.ticker_sec,
            "cik":                      r.cik_padded,
            "precio_usd":               None if pd.isna(r.precio_usd) else float(r.precio_usd),
            "currency":                 None if pd.isna(r.currency) else r.currency,
            "exchange":                 None if pd.isna(r.exchange) else r.exchange,
            "year_high":                None if pd.isna(r.year_high) else float(r.year_high),
            "year_low":                 None if pd.isna(r.year_low) else float(r.year_low),
            "dif_max_52w":              None if pd.isna(r.dif_max_52w) else float(r.dif_max_52w),
            "dif_min_52w":              None if pd.isna(r.dif_min_52w) else float(r.dif_min_52w),
            "per_ttm":                  None if pd.isna(r.per_ttm) else float(r.per_ttm),
            "eps_ttm_diluted":          None if pd.isna(r.eps_ttm_diluted) else float(r.eps_ttm_diluted),
            "margen_neto_ttm":          None if pd.isna(r.margen_neto_ttm) else float(r.margen_neto_ttm),
            "roe_cagr_5y":              None if pd.isna(r.roe_cagr_5y) else float(r.roe_cagr_5y),
            "deuda_lp_sobre_ebitda":    None if pd.isna(r.deuda_lp_sobre_ebitda) else float(r.deuda_lp_sobre_ebitda),
            "deuda_total_sobre_ebitda": None if pd.isna(r.deuda_total_sobre_ebitda) else float(r.deuda_total_sobre_ebitda),
            "fcfonce_equity_lp":        None if pd.isna(r.fcfonce_equity_lp) else float(r.fcfonce_equity_lp),
            "fcfonce_neto_caja":        None if pd.isna(r.fcfonce_neto_caja) else float(r.fcfonce_neto_caja),
            "payout_ttm":               None if pd.isna(r.payout_ttm) else float(r.payout_ttm),
            "cagr_eps_5y":              None if pd.isna(r.cagr_eps_5y) else float(r.cagr_eps_5y),
            "revenue_ttm":              None if pd.isna(r.revenue_ttm) else float(r.revenue_ttm),
            "netincome_ttm":            None if pd.isna(r.netincome_ttm) else float(r.netincome_ttm),
            "ebitda_ttm":               None if pd.isna(r.ebitda_ttm) else float(r.ebitda_ttm),
            "fcf_ttm":                  None if pd.isna(r.fcf_ttm) else float(r.fcf_ttm),
            "diluted_shares":           None if pd.isna(r.diluted_shares) else float(r.diluted_shares),
            "equity":                   None if pd.isna(r.equity) else float(r.equity),
            "lt_debt":                  None if pd.isna(r.lt_debt) else float(r.lt_debt),
            "deuda_total":              None if pd.isna(r.deuda_total) else float(r.deuda_total),
        })
    db.execute(RatioQuarterly.__table__.insert(), rows)
    db.commit()
    print(f"  ratios_quarterly inserted: {len(rows)}")


def main():
    if IS_SQLITE:
        print("ERROR: DATABASE_URL apunta a SQLite. Necesito Postgres como destino.")
        sys.exit(1)

    if not EXPORT_DIR.exists():
        print(f"ERROR: No existe {EXPORT_DIR}")
        sys.exit(1)

    manifest = json.loads((EXPORT_DIR / "manifest.json").read_text(encoding="utf-8"))
    generated_at = manifest.get("generated_at", "")
    as_of_date   = date.fromisoformat(generated_at[:10]) if generated_at else date.today()

    print(f"VALUARTY_DIR : {VALUARTY_DIR}")
    print(f"EXPORT_DIR   : {EXPORT_DIR}")
    print(f"dataset      : {manifest.get('dataset')} v{manifest.get('version')}")
    print(f"generated_at : {generated_at} (period_end={as_of_date})")

    db = SessionLocal()
    try:
        # === TRUNCATE en orden de FK ===
        print("\n[1/5] TRUNCATE tablas destino...")
        for tbl in ["ratios_quarterly", "fundamentals_raw", "prices_daily", "companies"]:
            db.execute(text(f"TRUNCATE TABLE {tbl} CASCADE"))
        db.commit()
        print("  ok")

        print("\n[2/5] Cargando companies...")
        sec_to_bymas = load_companies(db, EXPORT_DIR / "company_master.csv")

        print("\n[3/5] Cargando prices_daily...")
        load_prices(db, sec_to_bymas)

        print("\n[4/5] Cargando fundamentals_raw...")
        load_fundamentals_raw(db, EXPORT_DIR / "quarterly_fundamentals.csv")

        print("\n[5/5] Cargando ratios_quarterly...")
        load_ratios_snapshot(db, EXPORT_DIR / "ratio_snapshots.csv", as_of_date)

        # === Resumen final ===
        print("\n=== Resumen final ===")
        for tbl in ["companies", "prices_daily", "fundamentals_raw", "ratios_quarterly"]:
            n = db.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
            print(f"  {tbl:25s} : {n:>10,}")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
