"""
Migra los datos legacy de SQLite (data/argentina.db) al nuevo schema de Postgres.

Mapeo:
  - company_master  → companies
  - ratio_snapshots → ratios_quarterly  (1 fila por ticker con period_end = today)

Uso:
    # Postgres ya levantado via docker-compose (POSTGRES_PORT=5544 default)
    cd argfy/backend
    DATABASE_URL=postgresql+psycopg2://argfy:argfy_dev@localhost:5544/argfy \\
        python scripts/migrate_sqlite_to_pg.py

Idempotente: borra companies + ratios_quarterly (CASCADE) antes de insertar.
"""
import os
import sys
import sqlite3
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]   # argfy/backend/
sys.path.insert(0, str(ROOT))

from app.database import engine, SessionLocal, IS_SQLITE  # noqa: E402
from app.models import Company, RatioQuarterly             # noqa: E402

SQLITE_PATH = ROOT / "data" / "argentina.db"


def main():
    if IS_SQLITE:
        print(f"ERROR: DATABASE_URL apunta a SQLite. Necesito Postgres como destino.")
        print(f"Setea DATABASE_URL=postgresql+psycopg2://argfy:argfy_dev@localhost:5544/argfy")
        sys.exit(1)

    if not SQLITE_PATH.exists():
        print(f"ERROR: No existe {SQLITE_PATH}")
        sys.exit(1)

    print(f"Origen : sqlite://{SQLITE_PATH}")
    print(f"Destino: {engine.url}")

    src = sqlite3.connect(SQLITE_PATH)
    src.row_factory = sqlite3.Row

    # === Inventario origen ===
    cm_rows = src.execute("SELECT * FROM company_master").fetchall()
    rs_rows = src.execute("SELECT * FROM ratio_snapshots").fetchall()
    print(f"\nSQLite legacy:")
    print(f"  company_master  : {len(cm_rows)}")
    print(f"  ratio_snapshots : {len(rs_rows)}")

    # === Limpiar destino (cascade) ===
    db = SessionLocal()
    try:
        n_r = db.query(RatioQuarterly).delete()
        n_c = db.query(Company).delete()
        db.commit()
        print(f"\nDestino limpiado (ratios_quarterly={n_r}, companies={n_c}).")

        # === Migrar companies ===
        # source_tier=1 si tenía financials (vino de SEC), 4 si no.
        for r in cm_rows:
            c = Company(
                byma_ticker  = r["byma_ticker"],
                ticker_sec   = r["ticker_sec"],
                cik          = r["cik"],
                nombre       = r["nombre"],
                exchange     = r["exchange"],
                country      = "US" if r["cik"] else None,
                currency     = "USD" if r["cik"] else None,
                source_tier  = 1 if r["has_financials"] else 4,
                has_sec      = bool(r["has_financials"]),
                has_yf       = bool(r["has_prices"]),
                has_fmp      = False,
            )
            db.add(c)
        db.commit()
        print(f"  companies        : {len(cm_rows)} insertadas")

        # === Migrar ratio_snapshots → ratios_quarterly ===
        # period_end = today (snapshot único, primera fila de la historia)
        today = date.today()
        snapshot_as_of = datetime.utcnow()
        n_rq = 0
        skipped = 0
        seen = set()
        for r in rs_rows:
            byma = r["byma_ticker"]
            if byma in seen:
                skipped += 1
                continue
            seen.add(byma)
            rq = RatioQuarterly(
                byma_ticker              = byma,
                period_end               = today,
                as_of                    = snapshot_as_of,
                ticker_sec               = r["ticker_sec"],
                cik                      = r["cik"],
                precio_usd               = r["precio_usd"],
                currency                 = r["currency"],
                exchange                 = r["exchange"],
                year_high                = r["year_high"],
                year_low                 = r["year_low"],
                dif_max_52w              = r["dif_max_52w"],
                dif_min_52w              = r["dif_min_52w"],
                per_ttm                  = r["per_ttm"],
                eps_ttm_diluted          = r["eps_ttm_diluted"],
                margen_neto_ttm          = r["margen_neto_ttm"],
                roe_cagr_5y              = r["roe_cagr_5y"],
                deuda_lp_sobre_ebitda    = r["deuda_lp_sobre_ebitda"],
                deuda_total_sobre_ebitda = r["deuda_total_sobre_ebitda"],
                fcfonce_equity_lp        = r["fcfonce_equity_lp"],
                fcfonce_neto_caja        = r["fcfonce_neto_caja"],
                payout_ttm               = r["payout_ttm"],
                cagr_eps_5y              = r["cagr_eps_5y"],
                revenue_ttm              = r["revenue_ttm"],
                netincome_ttm            = r["netincome_ttm"],
                ebitda_ttm               = r["ebitda_ttm"],
                fcf_ttm                  = r["fcf_ttm"],
                diluted_shares           = r["diluted_shares"],
                equity                   = r["equity"],
                lt_debt                  = r["lt_debt"],
                deuda_total              = r["deuda_total"],
            )
            db.add(rq)
            n_rq += 1
        db.commit()
        print(f"  ratios_quarterly : {n_rq} insertadas (skipped duplicados: {skipped})")

        # === Sanity check ===
        c_count = db.query(Company).count()
        r_count = db.query(RatioQuarterly).count()
        print(f"\nFinal en Postgres:")
        print(f"  companies        : {c_count}")
        print(f"  ratios_quarterly : {r_count}")

        # Una empresa concreta para verificar
        aapl = db.query(RatioQuarterly).filter_by(byma_ticker="AAPL").first()
        if aapl:
            print(f"\nAAPL OK: PER={aapl.per_ttm:.2f}, ROE5y={aapl.roe_cagr_5y:.3f}, "
                  f"period_end={aapl.period_end}")

        print(f"\nMigración OK. Probá:")
        print(f"  curl http://localhost:8000/api/v1/fundamentals/coverage")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()
        src.close()


if __name__ == "__main__":
    main()
