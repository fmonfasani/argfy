"""
Daily job: refresh_prices
Actualiza precios diarios desde yfinance para todos los tickers US y BYMA.
Schedule: Diario 07:00 UTC | Duración ~5min | UPSERT por (byma_ticker, date)
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import PriceDaily

logger = logging.getLogger(__name__)

JOB_NAME = "refresh_prices"

def run(session: Session, run_id: str):
    """Fetch latest prices from yfinance for all tracked tickers."""
    logger.info("Starting refresh_prices ...")

    rows_inserted = 0
    rows_updated = 0
    errors = 0

    try:
        import yfinance as yf
    except ImportError:
        logger.error("yfinance not installed")
        return

    # Get unique tickers from PriceDaily + Company
    tickers = [
        row[0] for row in session.query(PriceDaily.byma_ticker).distinct().all()
    ]
    if not tickers:
        logger.warning("No tickers found in PriceDaily")
        return

    # Add tickers from Company table
    try:
        from ..models import Company
        company_tickers = [c.byma_ticker for c in session.query(Company.byma_ticker).all()]
        for t in company_tickers:
            if t not in tickers:
                tickers.append(t)
    except Exception:
        pass

    end = datetime.now()
    start = end - timedelta(days=7)

    for ticker in tickers:
        try:
            data = yf.download(ticker, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), progress=False)
            if data.empty:
                continue
            for date_idx, row in data.iterrows():
                date_val = date_idx.to_pydatetime().date() if hasattr(date_idx, "to_pydatetime") else date_idx.date()
                existing = session.query(PriceDaily).filter_by(byma_ticker=ticker, date=date_val).first()
                if existing:
                    existing.open = float(row["Open"]) if "Open" in row else existing.open
                    existing.high = float(row["High"]) if "High" in row else existing.high
                    existing.low = float(row["Low"]) if "Low" in row else existing.low
                    existing.close = float(row["Close"]) if "Close" in row else existing.close
                    existing.adj_close = float(row["Adj Close"]) if "Adj Close" in row else existing.adj_close
                    existing.volume = int(row["Volume"]) if "Volume" in row else existing.volume
                    rows_updated += 1
                else:
                    p = PriceDaily(
                        byma_ticker=ticker,
                        date=date_val,
                        open=float(row["Open"]) if "Open" in row else None,
                        high=float(row["High"]) if "High" in row else None,
                        low=float(row["Low"]) if "Low" in row else None,
                        close=float(row["Close"]) if "Close" in row else None,
                        adj_close=float(row["Adj Close"]) if "Adj Close" in row else None,
                        volume=int(row["Volume"]) if "Volume" in row else None,
                    )
                    session.add(p)
                    rows_inserted += 1
            session.commit()
        except Exception as e:
            logger.warning(f"Error fetching {ticker}: {e}")
            errors += 1
            session.rollback()

    logger.info(f"refresh_prices done: {rows_inserted} inserted, {rows_updated} updated, {errors} errors")
