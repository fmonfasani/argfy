"""
Seed idempotente de PlanFeature.
Corre en el lifespan de FastAPI. INSERT ON CONFLICT DO NOTHING.
"""
import logging
from sqlalchemy.orm import Session
from app.models import PlanFeature

logger = logging.getLogger(__name__)

PLAN_FEATURES: dict[str, list[str]] = {
    "free":       ["screener_basic"],
    "pro":        ["screener_basic", "historical_prices", "metric_history", "csv_export"],
    "enterprise": ["screener_basic", "historical_prices", "metric_history",
                   "csv_export", "api_access", "team_invitations", "admin_etl_trigger"],
}


def seed_plans(db: Session):
    existing = db.query(PlanFeature).count()
    if existing > 0:
        logger.info(f"Plan features already seeded ({existing} rows), skipping")
        return

    for plan, features in PLAN_FEATURES.items():
        for fk in features:
            db.add(PlanFeature(plan=plan, feature_key=fk, enabled=True))

    db.commit()
    logger.info(f"Seeded {sum(len(v) for v in PLAN_FEATURES.values())} plan features")
