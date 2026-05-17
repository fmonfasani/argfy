"""
FastAPI dependency: get_current_user from JWT or API key.
"""
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ApiKey, User
from ..services.auth import decode_access_token, hash_api_key

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    token = credentials.credentials

    # Try JWT first
    payload = decode_access_token(token)
    if payload:
        user = db.query(User).filter(User.id == payload.get("sub")).first()
        if user and user.is_active:
            return user
        raise HTTPException(status_code=401, detail="Invalid or inactive user")

    # Try API key
    key_hash = hash_api_key(token)
    api_key = db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()
    if api_key:
        user = (
            db.query(User)
            .filter(User.tenant_id == api_key.tenant_id, User.role == "admin")
            .first()
        )
        if user:
            api_key.last_used = datetime.utcnow()
            db.commit()
            return user

    raise HTTPException(status_code=401, detail="Invalid token or API key")
