"""
Seed de fundamentals para argfy.

Lee los outputs del pipeline de valuarty (cedears_con_cik.json + seguimiento.json)
y popula las tablas:
- company_master   (1 fila por byma_ticker, con flags de cobertura)
- ratio_snapshots  (1 fila por byma_ticker con los ratios calculados)

Uso (desde argfy/backend/):
    python scripts/seed_fundamentals.py

Path por defecto: ../../  (la raíz de valuarty/)
Override:        VALUARTY_DIR=/path/to/valuarty python scripts/seed_fundamentals.py
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Asegurar que podemos importar `app.*` cuando se corre desde argfy/backend/
ROOT = Path(__file__).resolve().parents[1]   # argfy/backend/
sys.path.insert(0, str(ROOT))

from app.database import engine, Base, SessionLocal  # noqa: E402
from app.models import CompanyMaster, RatioSnapshot  # noqa: E402


VALUARTY_DIR = Path(os.getenv("VALUARTY_DIR", ROOT.parent.parent))
CEDEARS_F    = VALUARTY_DIR / "cedears_con_cik.json"
SEGUIM_F     = VALUARTY_DIR / "seguimiento.json"


def main():
    print(f"VALUARTY_DIR : {VALUARTY_DIR}")
    print(f"cedears file : {CEDEARS_F}  exists={CEDEARS_F.exists()}")
    print(f"seguimiento  : {SEGUIM_F}   exists={SEGUIM_F.exists()}")

    if not CEDEARS_F.exists() or not SEGUIM_F.exists():
        print("\nERROR: Archivos de valuarty no encontrados.")
        print("Corre antes en valuarty/: python 03_*.py && python 04_*.py && python 05_*.py")
        sys.exit(1)

    # Crear tablas (idempotente)
    Base.metadata.create_all(bind=engine)
    print("\nTablas verificadas.")

    with open(CEDEARS_F, encoding="utf-8") as f:
        cedears_raw = json.load(f)["cedears"]
    with open(SEGUIM_F, encoding="utf-8") as f:
        filas = json.load(f)["filas"]

    print(f"\nCEDEARs en mapeo : {len(cedears_raw)}")
    print(f"Filas en seguim. : {len(filas)}")

    # Index seguimiento por byma_ticker
    by_byma = {f["byma_ticker"]: f for f in filas}

    db = SessionLocal()
    try:
        # Limpiar snapshots previos (reescribimos en cada seed)
        db.query(RatioSnapshot).delete()
        db.query(CompanyMaster).delete()
        db.commit()
        print("Tablas limpiadas.")

        now = datetime.utcnow()
        cm_count, rs_count = 0, 0

        for c in cedears_raw:
            byma = c.get("byma_ticker")
            if not byma:
                continue
            seg = by_byma.get(byma)

            # CompanyMaster (incluye los que no tienen financials)
            cm = CompanyMaster(
                byma_ticker    = byma,
                ticker_sec     = c.get("ticker_sec"),
                cik            = c.get("cik"),
                nombre         = c.get("nombre_sec"),
                exchange       = (seg or {}).get("exchange"),
                has_financials = bool(seg),
                has_prices     = bool((seg or {}).get("precio_usd")),
            )
            db.add(cm)
            cm_count += 1

            # RatioSnapshot solo si tenemos seguimiento
            if not seg:
                continue

            rs = RatioSnapshot(
                byma_ticker              = byma,
                ticker_sec               = seg.get("ticker_sec"),
                cik                      = seg.get("cik"),
                as_of                    = now,
                precio_usd               = seg.get("precio_usd"),
                currency                 = seg.get("currency"),
                exchange                 = seg.get("exchange"),
                year_high                = seg.get("year_high"),
                year_low                 = seg.get("year_low"),
                dif_max_52w              = seg.get("dif_max_52w"),
                dif_min_52w              = seg.get("dif_min_52w"),
                per_ttm                  = seg.get("per_ttm"),
                eps_ttm_diluted          = seg.get("eps_ttm_diluted"),
                margen_neto_ttm          = seg.get("margen_neto_ttm"),
                roe_cagr_5y              = seg.get("roe_cagr_5y"),
                deuda_lp_sobre_ebitda    = seg.get("deuda_lp_sobre_ebitda"),
                deuda_total_sobre_ebitda = seg.get("deuda_total_sobre_ebitda"),
                fcfonce_equity_lp        = seg.get("fcfonce_equity_lp"),
                fcfonce_neto_caja        = seg.get("fcfonce_neto_caja"),
                payout_ttm               = seg.get("payout_ttm"),
                cagr_eps_5y              = seg.get("cagr_eps_5y"),
                revenue_ttm              = seg.get("_revenue_ttm"),
                netincome_ttm            = seg.get("_netincome_ttm"),
                ebitda_ttm               = seg.get("_ebitda_ttm"),
                fcf_ttm                  = seg.get("_fcf_ttm"),
                diluted_shares           = seg.get("_diluted_shares"),
                equity                   = seg.get("_equity"),
                lt_debt                  = seg.get("_lt_debt"),
                deuda_total              = seg.get("_deuda_total"),
            )
            db.add(rs)
            rs_count += 1

        db.commit()

        print(f"\nInsertado:")
        print(f"  company_master   : {cm_count}")
        print(f"  ratio_snapshots  : {rs_count}")
        print(f"\nSeed OK. Probá: curl http://localhost:8000/api/v1/fundamentals/coverage")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
