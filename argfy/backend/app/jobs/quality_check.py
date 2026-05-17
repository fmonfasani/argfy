"""
Daily job: quality_check
Verifica cobertura de datos, consistencia y genera alertas.
Schedule: Diario 07:30 UTC | Duración ~2min
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import SessionLocal
from ..models import Company, RatioQuarterly, PriceDaily

logger = logging.getLogger(__name__)

JOB_NAME = "quality_check"

def run(session: Session, run_id: str):
    """Run data quality checks and log results."""
    logger.info("Starting quality_check ...")

    warnings = 0
    errors = 0

    total_companies = session.query(Company).count()
    companies_with_ratios = session.query(RatioQuarterly.byma_ticker).distinct().count()
    companies_with_prices = session.query(PriceDaily.byma_ticker).distinct().count()

    max_price_date = session.query(func.max(PriceDaily.date)).scalar()
    stale_prices = False
    if max_price_date:
        days_since = (datetime.now().date() - max_price_date).days
        if days_since > 2:
            logger.warning(f"Prices stale: last update was {days_since} days ago")
            stale_prices = True
            warnings += 1

    coverage_pct = round(companies_with_ratios / total_companies * 100, 1) if total_companies else 0

    if coverage_pct < 50:
        logger.warning(f"Low ratio coverage: {coverage_pct}%")
        warnings += 1

    logger.info(
        f"quality_check done: {total_companies} companies, "
        f"{companies_with_ratios} with ratios ({coverage_pct}%), "
        f"{companies_with_prices} with prices, "
        f"stale={'yes' if stale_prices else 'no'}, "
        f"{warnings} warnings, {errors} errors"
    )
