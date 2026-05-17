"""
Admin endpoints for ETL management + Dashboard + Team + Billing.
"""
import uuid
import logging
import secrets
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import ETLRun, User, Invitation, ApiKey, Subscription, APIUsage
from ..scheduler import JOB_REGISTRY, execute_job
from ..middleware.auth import get_current_user
from ..config.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

# ── Overview Dashboard ──────────────────────────────────

@router.get("/overview")
def admin_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(403, detail="Admin access required")

    tenant_id = current_user.tenant_id
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    api_calls_today = (
        db.query(func.count(APIUsage.id))
        .filter(APIUsage.timestamp >= today_start)
        .scalar()
        or 0
    )

    active_users = (
        db.query(func.count(User.id))
        .filter(User.tenant_id == tenant_id, User.is_active == True)
        .scalar()
        or 0
    )

    sub = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == tenant_id)
        .order_by(Subscription.created_at.desc())
        .first()
    )

    etl_runs_today = (
        db.query(func.count(ETLRun.id))
        .filter(ETLRun.scheduled_for == date.today())
        .scalar()
        or 0
    )

    return {
        "tenant_id": tenant_id,
        "plan": sub.plan if sub else "free",
        "api_calls_today": api_calls_today,
        "active_users": active_users,
        "etl_runs_today": etl_runs_today,
        "subscription_status": sub.status if sub else "active",
    }


# ── Team Management ──────────────────────────────────────

@router.get("/users")
def list_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(403, detail="Admin access required")

    users = (
        db.query(User)
        .filter(User.tenant_id == current_user.tenant_id)
        .order_by(User.created_at.desc())
        .all()
    )
    return {
        "data": [
            {
                "id": u.id,
                "email": u.email,
                "nombre": u.nombre,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ]
    }


@router.post("/invitations")
def create_invitation(
    email: str = Body(..., embed=True),
    role: str = Body("member", embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(403, detail="Admin access required")

    token = secrets.token_urlsafe(32)
    inv = Invitation(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        email=email,
        role=role,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=72),
    )
    db.add(inv)
    db.commit()

    return {
        "id": inv.id,
        "email": inv.email,
        "role": inv.role,
        "token": token,
        "expires_at": inv.expires_at.isoformat(),
    }


@router.delete("/invitations/{token}")
def revoke_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(403, detail="Admin access required")

    inv = (
        db.query(Invitation)
        .filter(
            Invitation.token == token,
            Invitation.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not inv:
        raise HTTPException(404, detail="Invitation not found")

    db.delete(inv)
    db.commit()
    return {"message": "Invitation revoked"}


# ── API Keys Management ─────────────────────────────────

@router.get("/api-keys")
def list_admin_api_keys(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(403, detail="Admin access required")

    keys = (
        db.query(ApiKey)
        .filter(ApiKey.tenant_id == current_user.tenant_id)
        .order_by(ApiKey.created_at.desc())
        .all()
    )
    return {
        "data": [
            {
                "id": k.id,
                "key_prefix": k.key_prefix,
                "name": k.name,
                "last_used": k.last_used.isoformat() if k.last_used else None,
                "created_at": k.created_at.isoformat() if k.created_at else None,
            }
            for k in keys
        ]
    }


@router.post("/api-keys")
def create_admin_api_key(
    name: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(403, detail="Admin access required")

    from ..services.auth import generate_api_key

    raw, prefix, key_hash = generate_api_key()
    api_key = ApiKey(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        key_hash=key_hash,
        key_prefix=prefix,
        name=name,
    )
    db.add(api_key)
    db.commit()

    return {"id": api_key.id, "key_prefix": prefix, "raw_key": raw, "name": name}


@router.delete("/api-keys/{key_id}")
def revoke_admin_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(403, detail="Admin access required")

    key = (
        db.query(ApiKey)
        .filter(ApiKey.id == key_id, ApiKey.tenant_id == current_user.tenant_id)
        .first()
    )
    if not key:
        raise HTTPException(404, detail="API key not found")

    db.delete(key)
    db.commit()
    return {"message": "API key revoked"}


# ── Billing History ──────────────────────────────────────

@router.get("/billing")
def admin_billing(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(403, detail="Admin access required")

    subs = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == current_user.tenant_id)
        .order_by(Subscription.created_at.desc())
        .all()
    )

    return {
        "data": [
            {
                "id": s.id,
                "plan": s.plan,
                "status": s.status,
                "current_period_start": s.current_period_start.isoformat() if s.current_period_start else None,
                "current_period_end": s.current_period_end.isoformat() if s.current_period_end else None,
                "cancel_at_period_end": s.cancel_at_period_end,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in subs
        ]
    }


# ── ETL Management (relocated under /admin) ─────────────

@router.get("/etl/last-runs")
def last_runs(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    rows = (
        db.query(ETLRun)
        .order_by(ETLRun.started_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "count": len(rows),
        "data": [
            {
                "id": r.id,
                "job_name": r.job_name,
                "trigger": r.trigger,
                "status": r.status,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "finished_at": r.finished_at.isoformat() if r.finished_at else None,
                "scheduled_for": r.scheduled_for.isoformat() if r.scheduled_for else None,
                "duration_ms": r.duration_ms,
                "rows_inserted": r.rows_inserted,
                "rows_updated": r.rows_updated,
                "errors_count": r.errors_count,
            }
            for r in rows
        ],
    }


@router.post("/etl/trigger/{job_name}")
def trigger_job(job_name: str, db: Session = Depends(get_db)):
    if job_name not in JOB_REGISTRY:
        raise HTTPException(404, detail=f"Unknown job: {job_name}")
    existing = (
        db.query(ETLRun)
        .filter(
            ETLRun.job_name == job_name,
            ETLRun.scheduled_for == date.today(),
            ETLRun.status == "running",
        )
        .first()
    )
    if existing:
        raise HTTPException(409, detail=f"Job {job_name} is already running today")
    execute_job(job_name, trigger="manual")
    return {"message": f"Job {job_name} triggered", "job_name": job_name}


@router.get("/etl/status")
def etl_status(db: Session = Depends(get_db)):
    from ..scheduler import scheduler
    jobs = sorted(JOB_REGISTRY.keys())
    last_runs = {}
    for jn in jobs:
        row = (
            db.query(ETLRun)
            .filter(ETLRun.job_name == jn)
            .order_by(ETLRun.started_at.desc())
            .first()
        )
        if row:
            last_runs[jn] = {
                "status": row.status,
                "started_at": row.started_at.isoformat() if row.started_at else None,
                "finished_at": row.finished_at.isoformat() if row.finished_at else None,
                "duration_ms": row.duration_ms,
            }
        else:
            last_runs[jn] = None
    return {
        "scheduler_running": scheduler.running,
        "registered_jobs": jobs,
        "last_runs": last_runs,
    }


@router.get("/last-runs")
def last_runs(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """Return the most recent ETL run records."""
    rows = (
        db.query(ETLRun)
        .order_by(ETLRun.started_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "count": len(rows),
        "data": [
            {
                "id": r.id,
                "job_name": r.job_name,
                "trigger": r.trigger,
                "status": r.status,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "finished_at": r.finished_at.isoformat() if r.finished_at else None,
                "scheduled_for": r.scheduled_for.isoformat() if r.scheduled_for else None,
                "duration_ms": r.duration_ms,
                "rows_inserted": r.rows_inserted,
                "rows_updated": r.rows_updated,
                "errors_count": r.errors_count,
            }
            for r in rows
        ],
    }


@router.post("/trigger/{job_name}")
def trigger_job(job_name: str, db: Session = Depends(get_db)):
    """Manually trigger an ETL job."""
    if job_name not in JOB_REGISTRY:
        raise HTTPException(404, detail=f"Unknown job: {job_name}")

    # Check for existing run today
    existing = (
        db.query(ETLRun)
        .filter(
            ETLRun.job_name == job_name,
            ETLRun.scheduled_for == date.today(),
            ETLRun.status == "running",
        )
        .first()
    )
    if existing:
        raise HTTPException(409, detail=f"Job {job_name} is already running today")

    execute_job(job_name, trigger="manual")

    return {"message": f"Job {job_name} triggered", "job_name": job_name}


@router.get("/status")
def etl_status(db: Session = Depends(get_db)):
    """Return last-run status per job + scheduler info."""
    from ..scheduler import scheduler

    jobs = sorted(JOB_REGISTRY.keys())
    last_runs = {}
    for jn in jobs:
        row = (
            db.query(ETLRun)
            .filter(ETLRun.job_name == jn)
            .order_by(ETLRun.started_at.desc())
            .first()
        )
        if row:
            last_runs[jn] = {
                "status": row.status,
                "started_at": row.started_at.isoformat() if row.started_at else None,
                "finished_at": row.finished_at.isoformat() if row.finished_at else None,
                "duration_ms": row.duration_ms,
            }
        else:
            last_runs[jn] = None

    return {
        "scheduler_running": scheduler.running,
        "registered_jobs": jobs,
        "last_runs": last_runs,
    }
