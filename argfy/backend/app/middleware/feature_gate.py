"""
Dependency function: 403 if tenant lacks a feature.
Uso: @router.get(..., dependencies=[Depends(require_feature("historical_prices"))])
"""
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.auth import has_feature
from .auth import get_current_user
from ..models import User


def require_feature(feature_key: str):
    def _check(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        if not has_feature(db, current_user.tenant_id, feature_key):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "feature_locked",
                    "feature": feature_key,
                    "upgrade_url": f"/pricing?feature={feature_key}",
                },
            )
        return current_user
    return _check
