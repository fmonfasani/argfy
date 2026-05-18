"""
Import del Seguimiento.xlsx -> tablas `companies` + `ratios_quarterly`.

Uso dentro del container backend:
    docker cp /tmp/Seguimiento.xlsx <backend>:/tmp/
    docker exec <backend> python -m scripts.import_seguimiento_xlsx

Override path:
    docker exec <backend> sh -c 'XLSX_PATH=/tmp/otro.xlsx python -m scripts.import_seguimiento_xlsx'
"""
import os
import sys
import re
from pathlib import Path
from datetime import date

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database import SessionLocal  # noqa: E402
from app.models import Company, RatioQuarterly  # noqa: E402


XLSX_PATH = os.getenv("XLSX_PATH", "/tmp/Seguimiento.xlsx")
PERIOD_END = date.fromisoformat(os.getenv("PERIOD_END", date.today().isoformat()))

PRECIO_RE = re.compile(r"[^\d,.\-]")


def parse_precio_usd(v):
    """'u$s 252,07' -> 252.07 / 'u$s 1.234,56' -> 1234.56"""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = PRECIO_RE.sub("", str(v))
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def to_float(v):
    if v is None or v == "":
        return None
    try:
        f = float(v)
        if pd.isna(f):
            return None
        return f
    except (ValueError, TypeError):
        return None


def to_str(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip()
    return s if s else None


def main():
    print(f"XLSX_PATH  : {XLSX_PATH}")
    print(f"PERIOD_END : {PERIOD_END}")

    if not Path(XLSX_PATH).exists():
        print(f"ERROR: xlsx no encontrado en {XLSX_PATH}")
        sys.exit(1)

    df = pd.read_excel(XLSX_PATH, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]
    print(f"Filas leidas: {len(df)}  Columnas: {list(df.columns)}")

    # Identificar columnas por posicion (orden fijo del Excel)
    cols = list(df.columns)
    if len(cols) < 15:
        print(f"ERROR: se esperaban 15 columnas, hay {len(cols)}")
        sys.exit(1)

    db = SessionLocal()
    n_comp = 0
    n_rat = 0
    skipped = 0

    try:
        for _, row in df.iterrows():
            ticker = to_str(row.iloc[0])
            if not ticker:
                skipped += 1
                continue

            exchange = to_str(row.iloc[1])

            db.merge(Company(
                byma_ticker=ticker,
                ticker_sec=ticker,
                exchange=exchange,
                country="US",
                currency="USD",
                source_tier=1,
                has_sec=False,
                has_yf=False,
                has_fmp=False,
            ))
            n_comp += 1

            db.merge(RatioQuarterly(
                byma_ticker=ticker,
                period_end=PERIOD_END,
                ticker_sec=ticker,
                exchange=exchange,
                currency="USD",
                precio_usd=parse_precio_usd(row.iloc[2]),
                per_ttm=to_float(row.iloc[3]),
                year_high=parse_precio_usd(row.iloc[4]),
                dif_max_52w=to_float(row.iloc[5]),
                year_low=parse_precio_usd(row.iloc[6]),
                dif_min_52w=to_float(row.iloc[7]),
                deuda_total_sobre_ebitda=to_float(row.iloc[8]),
                eps_ttm_diluted=to_float(row.iloc[9]),
                cagr_eps_5y=to_float(row.iloc[10]),
                margen_neto_ttm=to_float(row.iloc[11]),
                roe_cagr_5y=to_float(row.iloc[12]),
                fcfonce_equity_lp=to_float(row.iloc[13]),
                payout_ttm=to_float(row.iloc[14]),
            ))
            n_rat += 1

        db.commit()
        print(f"\nOK")
        print(f"  companies inserted/updated : {n_comp}")
        print(f"  ratios_quarterly           : {n_rat}")
        print(f"  filas vacias skip          : {skipped}")
        print(f"\nProba: curl https://api.argfy.com/api/v1/fundamentals/coverage")

    except Exception as e:
        db.rollback()
        print(f"ERROR durante import: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
