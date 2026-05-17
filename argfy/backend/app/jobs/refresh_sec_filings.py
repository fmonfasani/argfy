"""
Weekly job: refresh_sec_filings
Descarga nuevos filings 10-K/10-Q desde SEC EDGAR para CIKs tracked.
Schedule: Lunes 06:00 UTC | Duración ~10min | UPSERT por cik
"""
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import FundamentalRaw

logger = logging.getLogger(__name__)

JOB_NAME = "refresh_sec_filings"

SEC_BASE = "https://data.sec.gov"
USER_AGENT = "Argfy/1.0 (contact@argfy.com)"

def run(session: Session, run_id: str):
    """Refresh SEC filings for all tracked CIKs."""
    logger.info("Starting refresh_sec_filings ...")

    rows_inserted = 0
    rows_updated = 0
    errors = 0

    ciks = [
        row[0] for row in session.query(FundamentalRaw.cik).distinct().all()
    ]
    if not ciks:
        logger.warning("No CIKs found in FundamentalRaw")
        return

    import requests

    for cik in ciks:
        try:
            cik_padded = str(cik).zfill(10)
            url = f"{SEC_BASE}/cik/000{cik_padded}/companyfacts.json"
            headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
            resp = requests.get(url, headers=headers, timeout=30)

            if resp.status_code != 200:
                logger.warning(f"SEC returned {resp.status_code} for CIK {cik}")
                errors += 1
                continue

            payload = resp.json()

            existing = session.query(FundamentalRaw).filter_by(cik=str(cik)).first()
            if existing:
                existing.raw_data = payload
                existing.updated_at = datetime.utcnow()
                rows_updated += 1
            else:
                fr = FundamentalRaw(cik=str(cik), raw_data=payload)
                session.add(fr)
                rows_inserted += 1

            session.commit()

        except Exception as e:
            logger.warning(f"Error fetching CIK {cik}: {e}")
            errors += 1
            session.rollback()

    logger.info(f"refresh_sec_filings done: {rows_inserted} inserted, {rows_updated} updated, {errors} errors")
