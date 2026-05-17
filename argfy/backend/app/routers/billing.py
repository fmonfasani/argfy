"""
Billing router: Mercado Pago checkout, webhook, portal, cancel.
"""
import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Subscription
from ..middleware.auth import get_current_user
from ..services.billing import create_preference, handle_payment_approved, handle_subscription_cancelled

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


@router.post("/create-checkout")
def create_checkout(
    plan: str = Query(..., pattern="^(pro|enterprise)$"),
    current_user: User = Depends(get_current_user),
):
    """Crea una preferencia de pago en Mercado Pago y devuelve el init_point."""
    if plan not in ("pro", "enterprise"):
        raise HTTPException(400, detail="Invalid plan. Must be 'pro' or 'enterprise'")

    pref = create_preference(plan, current_user)
    if not pref:
        raise HTTPException(502, detail="Failed to create payment preference")

    return {
        "init_point": pref.get("init_point"),
        "sandbox_init_point": pref.get("sandbox_init_point"),
        "preference_id": pref.get("id"),
        "plan": plan,
    }


@router.post("/webhook/mp")
async def mp_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Mercado Pago IPN webhook.
    Handles payment approved and subscription cancelled events.
    """
    body = await request.body()
    x_signature = request.headers.get("x-signature", "")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(400, detail="Invalid JSON")

    event_type = data.get("type")
    action = data.get("action")

    # Payment approved
    if event_type == "payment" or action == "payment.created":
        payment_id = data.get("data", {}).get("id")
        if not payment_id:
            return {"status": "ignored"}

        import httpx
        from ..config.config import settings

        try:
            r = httpx.get(
                f"https://api.mercadopago.com/v1/payments/{payment_id}",
                headers={"Authorization": f"Bearer {settings.MP_ACCESS_TOKEN}"},
                timeout=10,
            )
            r.raise_for_status()
            payment = r.json()
        except Exception as e:
            logger.error(f"Failed to fetch payment {payment_id}: {e}")
            return {"status": "error"}

        if payment.get("status") == "approved":
            external_ref = payment.get("external_reference", "")
            mp_sub_id = payment.get("subscription_id")
            handle_payment_approved(db, external_ref, payment_id, mp_sub_id)

    # Subscription cancelled
    elif event_type == "subscription" or action == "subscription.cancelled":
        sub_id = data.get("data", {}).get("id")
        if sub_id:
            handle_subscription_cancelled(db, sub_id)

    return {"status": "ok"}


@router.get("/portal")
def billing_portal(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Devuelve información de facturación del usuario."""
    sub = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == current_user.tenant_id)
        .order_by(Subscription.created_at.desc())
        .first()
    )

    if not sub:
        return {
            "plan": "free",
            "status": "active",
            "cancel_at_period_end": False,
        }

    return {
        "subscription_id": sub.id,
        "plan": sub.plan,
        "status": sub.status,
        "cancel_at_period_end": sub.cancel_at_period_end,
        "current_period_start": sub.current_period_start.isoformat() if sub.current_period_start else None,
        "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
    }


@router.post("/cancel")
def cancel_subscription(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Marca la suscripción para cancelación al fin del período."""
    sub = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == current_user.tenant_id, Subscription.status == "active")
        .order_by(Subscription.created_at.desc())
        .first()
    )

    if not sub:
        raise HTTPException(404, detail="No active subscription found")

    if sub.plan == "free":
        raise HTTPException(400, detail="Free plan cannot be cancelled")

    sub.cancel_at_period_end = True
    db.commit()

    return {"message": "Subscription will be cancelled at period end", "cancel_at_period_end": True}
