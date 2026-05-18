"""
Auth service: JWT creation/verification, password hashing, Google OAuth.
"""
import uuid
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from ..config.config import settings
from ..models import User, Tenant, Subscription, ApiKey

logger = logging.getLogger(__name__)

ALGORITHM = settings.JWT_ALGORITHM
SECRET = settings.JWT_SECRET
EXPIRY_HOURS = settings.JWT_EXPIRY_HOURS


# ── Password ──────────────────────────────────────────────
# bcrypt limita passwords a 72 bytes. Truncamos defensivamente en ambos extremos.

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))


# ── JWT ───────────────────────────────────────────────────

def create_access_token(user_id: str, tenant_id: str, role: str) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=EXPIRY_HOURS),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None


# ── Tenant helpers ────────────────────────────────────────

def create_tenant(db: Session, name: str) -> Tenant:
    slug = name.lower().replace(" ", "-") + "-" + secrets.token_hex(4)
    tenant = Tenant(id=str(uuid.uuid4()), name=name, slug=slug)
    db.add(tenant)
    db.flush()

    sub = Subscription(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        plan="free",
        status="active",
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=365 * 10),
    )
    db.add(sub)
    return tenant


# ── User helpers ──────────────────────────────────────────

def create_user(
    db: Session,
    email: str,
    password: Optional[str] = None,
    google_id: Optional[str] = None,
    nombre: Optional[str] = None,
) -> User:
    tenant = create_tenant(db, email.split("@")[0])
    user = User(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        email=email,
        password_hash=hash_password(password) if password else None,
        google_id=google_id,
        nombre=nombre or email.split("@")[0],
        role="admin",
    )
    db.add(user)
    db.commit()
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    return db.query(User).filter(User.google_id == google_id).first()


def get_tenant_subscription(db: Session, tenant_id: str) -> Optional[Subscription]:
    return (
        db.query(Subscription)
        .filter(Subscription.tenant_id == tenant_id)
        .order_by(Subscription.created_at.desc())
        .first()
    )


# ── API Key helpers ───────────────────────────────────────

def generate_api_key() -> tuple[str, str, str]:
    raw = "argfy_" + secrets.token_hex(24)
    prefix = raw[:16]
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    return raw, prefix, key_hash


def hash_api_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


# ── Feature gate helper ───────────────────────────────────

def has_feature(db: Session, tenant_id: str, feature_key: str) -> bool:
    sub = get_tenant_subscription(db, tenant_id)
    if not sub:
        return False
    pf = (
        db.query(PlanFeature)
        .filter(PlanFeature.plan == sub.plan, PlanFeature.feature_key == feature_key)
        .first()
    )
    if pf is None:
        return False
    return pf.enabled
