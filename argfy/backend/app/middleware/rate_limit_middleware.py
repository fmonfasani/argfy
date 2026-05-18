"""
Rate limiter por plan usando slowapi.
Limits: free=10/min, pro=60/min, enterprise=300/min.
Key derivado de tenant_id (JWT) o IP (anónimo).
"""
import base64
import json
import logging
from typing import Optional

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from ..models import ApiKey
from ..database import SessionLocal

logger = logging.getLogger(__name__)

PLAN_LIMITS = {
    "free":       "10/minute",
    "pro":        "60/minute",
    "enterprise": "300/minute",
}


def _extract_jwt_payload(token: str) -> Optional[dict]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload_b64 = parts[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        decoded = base64.urlsafe_b64decode(payload_b64)
        return json.loads(decoded)
    except Exception:
        return None


def _get_tenant_id(request: Request) -> Optional[str]:
    tenant_id = getattr(request.state, "tenant_id", None)
    if tenant_id:
        return tenant_id
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        payload = _extract_jwt_payload(token)
        if payload:
            return payload.get("tenant_id")
    return None


def _get_plan_for_tenant(tenant_id: str) -> str:
    try:
        from ..services.auth import get_tenant_subscription
        db = SessionLocal()
        try:
            sub = get_tenant_subscription(db, tenant_id)
            if sub:
                return sub.plan
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Rate limiter: could not get plan for {tenant_id}: {e}")
    return "free"


def _get_plan_key(request: Request) -> str:
    tenant_id = _get_tenant_id(request)
    if tenant_id:
        plan = _get_plan_for_tenant(tenant_id)
        return f"{plan}:{tenant_id}"
    return f"anon:{get_remote_address(request)}"


def get_plan_limits(plan: str = "free") -> list[str]:
    return [PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])]


limiter = Limiter(key_func=_get_plan_key, default_limits=["60/minute"])


class RateLimitPlanMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        tenant_id = _get_tenant_id(request)
        if tenant_id:
            request.state.tenant_id = tenant_id
        response = await call_next(request)
        return response
