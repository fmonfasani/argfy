"""
Monthly job: recalc_ratios
Recalcula todos los ratios fundamentalistas desde FundamentalRaw.
Schedule: 1° del mes 04:00 UTC | Duración ~15min | UPSERT por (byma_ticker, period_end)
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Company, RatioQuarterly, FundamentalRaw

logger = logging.getLogger(__name__)

JOB_NAME = "recalc_ratios"

def run(session: Session, run_id: str):
    """Recalculate all quarterly ratios from raw SEC data."""
    logger.info("Starting recalc_ratios ...")

    rows_inserted = 0
    rows_updated = 0
    errors = 0

    companies = session.query(Company).filter(Company.has_sec == True).all()

    for company in companies:
        try:
            raw = session.query(FundamentalRaw).filter_by(cik=company.cik).first()
            if not raw:
                continue

            data = raw.raw_data if isinstance(raw.raw_data, dict) else {}
            facts = data.get("facts", {}).get("us-gaap", {})

            # Simplified ratio calculation — in production use the full calc module
            for period_end_str, metrics in _extract_quarterly(facts).items():
                existing = session.query(RatioQuarterly).filter_by(
                    byma_ticker=company.byma_ticker, period_end=period_end_str
                ).first()

                if existing:
                    for k, v in metrics.items():
                        if hasattr(existing, k) and v is not None:
                            setattr(existing, k, v)
                    rows_updated += 1
                else:
                    rq = RatioQuarterly(byma_ticker=company.byma_ticker, period_end=period_end_str, **metrics)
                    session.add(rq)
                    rows_inserted += 1

            session.commit()
        except Exception as e:
            logger.warning(f"Error recalc ratios for {company.byma_ticker}: {e}")
            errors += 1
            session.rollback()

    logger.info(f"recalc_ratios done: {rows_inserted} inserted, {rows_updated} updated, {errors} errors")


def _extract_quarterly(facts: dict) -> dict:
    """Extract quarterly metric snapshots from SEC facts. Simplified for MVP."""
    result = {}
    # Map GAAP concepts to RatioQuarterly columns
    gaap_map = {
        "RevenueFromContractWithCustomerExcludingAssessedTax": "revenue_ttm",
        "NetIncomeLoss": "netincome_ttm",
        "EarningsPerShareDiluted": "eps_ttm_diluted",
        "OperatingIncomeLoss": "ebitda_ttm",  # approximation
    }
    for gaap_key, col in gaap_map.items():
        series = facts.get(gaap_key, {}).get("units", {}).get("USD", [])
        for entry in series:
            period = entry.get("end")
            if not period:
                continue
            if period not in result:
                result[period] = {}
            result[period][col] = entry.get("val")
    return result
