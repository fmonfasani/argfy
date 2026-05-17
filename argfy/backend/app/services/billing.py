"""
Billing service: Mercado Pago checkout, webhook handling, subscription management.
"""
import uuid
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from ..config.config import settings
from ..models import Subscription, User

logger = logging.getLogger(__name__)

MP_API = "https://api.mercadopago.com"


def get_mp_headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.MP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def create_preference(plan: str, user: User) -> Optional[dict]:
    """Crea una preferencia de pago en Mercado Pago. Devuelve el init_point."""
    price_info = settings.PLAN_PRICES.get(plan)
    if not price_info:
        logger.error(f"Unknown plan: {plan}")
        return None

    external_ref = f"{user.tenant_id}::{plan}::{uuid.uuid4().hex[:8]}"

    payload = {
        "items": [
            {
                "title": price_info["title"],
                "description": price_info["description"],
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": float(price_info["price"]) / 100,
            }
        ],
        "payer": {"email": user.email},
        "back_urls": {
            "success": settings.MP_SUCCESS_URL,
            "failure": settings.MP_FAILURE_URL,
            "pending": settings.MP_PENDING_URL,
        },
        "auto_return": "approved",
        "external_reference": external_ref,
        "notification_url": f"{settings.MP_SUCCESS_URL.rsplit('/', 2)[0]}/api/v1/billing/webhook/mp",
    }

    try:
        r = httpx.post(
            f"{MP_API}/checkout/preferences",
            headers=get_mp_headers(),
            json=payload,
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        logger.info(f"MP preference created: {data.get('id')} for {user.email} ({plan})")
        return data
    except Exception as e:
        logger.error(f"MP create_preference failed: {e}")
        return None


def verify_webhook_signature(request_body: bytes, x_signature: str) -> bool:
    """HMAC-SHA256 verification of Mercado Pago webhook."""
    if not settings.MP_WEBHOOK_SECRET:
        logger.warning("MP_WEBHOOK_SECRET not set, skipping signature verification")
        return True
    expected = hmac.new(
        settings.MP_WEBHOOK_SECRET.encode(),
        request_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, x_signature)


def handle_payment_approved(db: Session, external_ref: str, mp_payment_id: str, mp_subscription_id: Optional[str] = None):
    """
    Procesa un pago aprobado de Mercado Pago.
    external_ref format: tenant_id::plan::random
    """
    try:
        tenant_id, plan, _ = external_ref.split("::")
    except ValueError:
        logger.error(f"Invalid external_reference: {external_ref}")
        return

    sub = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == tenant_id, Subscription.status == "active")
        .order_by(Subscription.created_at.desc())
        .first()
    )

    if sub:
        sub.plan = plan
        sub.mp_subscription_id = mp_subscription_id or sub.mp_subscription_id
        sub.current_period_start = datetime.utcnow()
        sub.current_period_end = datetime.utcnow() + timedelta(days=30)
        sub.status = "active"
        logger.info(f"Subscription upgraded to {plan} for tenant {tenant_id}")
    else:
        sub = Subscription(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            plan=plan,
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30),
            mp_subscription_id=mp_subscription_id,
        )
        db.add(sub)
        logger.info(f"Subscription created: {plan} for tenant {tenant_id}")

    db.commit()


def handle_subscription_cancelled(db: Session, mp_subscription_id: str):
    sub = (
        db.query(Subscription)
        .filter(Subscription.mp_subscription_id == mp_subscription_id)
        .first()
    )
    if sub:
        sub.cancel_at_period_end = True
        sub.status = "cancelled"
        db.commit()
        logger.info(f"Subscription cancelled: {sub.tenant_id}")
