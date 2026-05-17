"""
APScheduler setup for ETL cron jobs.
Arranca en lifespan de FastAPI. Protección anti-duplicados via UNIQUE(job_name, scheduled_for).
"""
import uuid
import logging
from datetime import datetime, date
from contextlib import asynccontextmanager

from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .database import SessionLocal
from .models import ETLRun

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone="UTC")

JOB_REGISTRY: dict[str, callable] = {}


def register_job(name: str, func: callable):
    """Register a job function so the scheduler and admin endpoint can call it."""
    JOB_REGISTRY[name] = func


def record_run(session, job_name: str, trigger: str, status: str = "running", **extra):
    """Create an ETLRun record, catching duplicate silently."""
    try:
        run = ETLRun(
            id=str(uuid.uuid4()),
            job_name=job_name,
            trigger=trigger,
            status=status,
            started_at=datetime.utcnow(),
            scheduled_for=date.today(),
            **extra
        )
        session.add(run)
        session.commit()
        return run.id
    except IntegrityError:
        session.rollback()
        logger.warning(f"Duplicate run skipped for {job_name} today")
        return None


def finish_run(session, run_id: str | None, status: str, **extra):
    """Mark an ETLRun as finished."""
    if not run_id:
        return
    run = session.query(ETLRun).filter_by(id=run_id).first()
    if run:
        run.status = status
        run.finished_at = datetime.utcnow()
        if extra.get("duration_ms"):
            run.duration_ms = extra["duration_ms"]
        run.rows_inserted = extra.get("rows_inserted", 0)
        run.rows_updated = extra.get("rows_updated", 0)
        run.errors_count = extra.get("errors_count", 0)
        session.commit()


def execute_job(job_name: str, trigger: str = "scheduled"):
    """Execute a registered job with ETLRun tracking."""
    func = JOB_REGISTRY.get(job_name)
    if not func:
        logger.error(f"No job registered: {job_name}")
        return

    session = SessionLocal()
    run_id = record_run(session, job_name, trigger)
    started = datetime.utcnow()

    try:
        func(session, run_id or "")
        duration = int((datetime.utcnow() - started).total_seconds() * 1000)
        finish_run(session, run_id, "success", duration_ms=duration)
        logger.info(f"Job {job_name} completed in {duration}ms")
    except Exception as e:
        duration = int((datetime.utcnow() - started).total_seconds() * 1000)
        finish_run(session, run_id, "failed", duration_ms=duration, errors_count=1)
        logger.error(f"Job {job_name} failed after {duration}ms: {e}")
    finally:
        session.close()


def start():
    """Configure and start the APScheduler."""
    if scheduler.running:
        return

    jobs = [
        ("refresh_prices",      CronTrigger(day_of_week="mon-sun", hour=7,  minute=0,  timezone="UTC")),
        ("quality_check",       CronTrigger(day_of_week="mon-sun", hour=7,  minute=30, timezone="UTC")),
        ("refresh_sec_filings", CronTrigger(day_of_week="mon",     hour=6,  minute=0,  timezone="UTC")),
        ("recalc_ratios",       CronTrigger(day="1",               hour=4,  minute=0,  timezone="UTC")),
    ]

    for job_name, trigger in jobs:
        if job_name not in JOB_REGISTRY:
            logger.warning(f"Job {job_name} not registered, skipping schedule")
            continue
        scheduler.add_job(
            execute_job,
            trigger=trigger,
            args=[job_name, "scheduled"],
            id=job_name,
            name=job_name,
            replace_existing=True,
            misfire_grace_time=300,
        )
        logger.info(f"Scheduled job: {job_name}")

    scheduler.start()
    logger.info("APScheduler started")


def stop():
    """Shut down the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")
