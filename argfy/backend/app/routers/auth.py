"""
Auth router: register, login, Google OAuth, me, refresh, api-keys.
"""
import uuid
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from ..database import get_db
from ..models import User, ApiKey as ApiKeyModel
from ..services.auth import (
    create_user,
    get_user_by_email,
    get_user_by_google_id,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_api_key,
    hash_api_key,
    get_tenant_subscription,
)
from ..middleware.auth import get_current_user
from ..config.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# ── Schemas ──────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str
    password: str
    nombre: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class GoogleAuthRequest(BaseModel):
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class ApiKeyResponse(BaseModel):
    id: str
    key_prefix: str
    name: str
    last_used: Optional[str] = None
    created_at: str


class ApiKeyCreateResponse(BaseModel):
    id: str
    key_prefix: str
    raw_key: str
    name: str


# ── Endpoints ────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if get_user_by_email(db, req.email):
        raise HTTPException(409, detail="Email already registered")

    user = create_user(db, email=req.email, password=req.password, nombre=req.nombre)
    token = create_access_token(user.id, user.tenant_id, user.role)

    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "email": user.email,
            "nombre": user.nombre,
            "role": user.role,
            "tenant_id": user.tenant_id,
        },
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, req.email)
    if not user or not user.password_hash:
        raise HTTPException(401, detail="Invalid email or password")

    if not verify_password(req.password, user.password_hash):
        raise HTTPException(401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(403, detail="Account is disabled")

    token = create_access_token(user.id, user.tenant_id, user.role)

    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "email": user.email,
            "nombre": user.nombre,
            "role": user.role,
            "tenant_id": user.tenant_id,
        },
    )


@router.post("/google", response_model=TokenResponse)
def google_auth(req: GoogleAuthRequest, db: Session = Depends(get_db)):
    import httpx
    google_token_url = "https://oauth2.googleapis.com/token"
    google_userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    try:
        r = httpx.post(
            google_token_url,
            data={
                "code": req.code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": "postmessage",
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        r.raise_for_status()
        token_data = r.json()
        access_token = token_data["access_token"]

        r2 = httpx.get(
            google_userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        r2.raise_for_status()
        profile = r2.json()
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        raise HTTPException(401, detail="Google authentication failed")

    google_id = profile["id"]
    email = profile.get("email", "")
    nombre = profile.get("name", "")

    user = get_user_by_google_id(db, google_id)
    if not user:
        existing = get_user_by_email(db, email)
        if existing:
            existing.google_id = google_id
            db.commit()
            user = existing
        else:
            user = create_user(db, email=email, google_id=google_id, nombre=nombre)

    if not user.is_active:
        raise HTTPException(403, detail="Account is disabled")

    token = create_access_token(user.id, user.tenant_id, user.role)

    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "email": user.email,
            "nombre": user.nombre,
            "role": user.role,
            "tenant_id": user.tenant_id,
        },
    )


@router.get("/me")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sub = get_tenant_subscription(db, current_user.tenant_id)
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nombre": current_user.nombre,
        "role": current_user.role,
        "tenant_id": current_user.tenant_id,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "subscription": {
            "plan": sub.plan if sub else "free",
            "status": sub.status if sub else "active",
            "current_period_end": sub.current_period_end.isoformat() if sub and sub.current_period_end else None,
        } if sub else None,
    }


@router.post("/refresh")
def refresh_token(current_user: User = Depends(get_current_user)):
    token = create_access_token(current_user.id, current_user.tenant_id, current_user.role)
    return {"access_token": token, "token_type": "bearer"}


# ── API Key management ──────────────────────────────────

@router.get("/api-keys")
def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    keys = (
        db.query(ApiKeyModel)
        .filter(ApiKeyModel.tenant_id == current_user.tenant_id)
        .order_by(ApiKeyModel.created_at.desc())
        .all()
    )
    return {
        "data": [
            ApiKeyResponse(
                id=k.id,
                key_prefix=k.key_prefix,
                name=k.name,
                last_used=k.last_used.isoformat() if k.last_used else None,
                created_at=k.created_at.isoformat() if k.created_at else None,
            )
            for k in keys
        ]
    }


@router.post("/api-keys", response_model=ApiKeyCreateResponse)
def create_api_key(
    name: str = Query(..., description="A name for this key"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    raw, prefix, key_hash = generate_api_key()
    api_key = ApiKeyModel(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        key_hash=key_hash,
        key_prefix=prefix,
        name=name,
    )
    db.add(api_key)
    db.commit()

    return ApiKeyCreateResponse(
        id=api_key.id,
        key_prefix=prefix,
        raw_key=raw,
        name=name,
    )


@router.delete("/api-keys/{key_id}")
def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    api_key = (
        db.query(ApiKeyModel)
        .filter(
            ApiKeyModel.id == key_id,
            ApiKeyModel.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not api_key:
        raise HTTPException(404, detail="API key not found")

    db.delete(api_key)
    db.commit()
    return {"message": "API key revoked"}
