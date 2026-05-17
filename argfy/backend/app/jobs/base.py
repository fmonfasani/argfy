"""Job base utilities."""
import uuid
import logging
from datetime import datetime, date
from functools import wraps

logger = logging.getLogger(__name__)


def run_job(func):
    """Decorator that wraps a job function with ETLRun tracking."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        run_id = str(uuid.uuid4())
        job_name = func.__name__
        logger.info(f"[{run_id}] Starting job {job_name}")
        try:
            result = func(*args, run_id=run_id, **kwargs)
            logger.info(f"[{run_id}] Job {job_name} completed")
            return result
        except Exception as e:
            logger.error(f"[{run_id}] Job {job_name} failed: {e}")
            raise
    return wrapper
