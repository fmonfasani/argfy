"""
Rate limiter por plan usando slowapi.
Limits: free=10/min, pro=60/min, enterprise=300/min.
Key derivado de tenant_id (JWT) o IP (anónimo).
"""
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def _get_plan_key(request: Request) -> str:
    tenant_id = getattr(request.state, "tenant_id", None)
    if tenant_id:
        return tenant_id
    return get_remote_address(request)


PLAN_LIMITS = {
    "free":       "10/minute",
    "pro":        "60/minute",
    "enterprise": "300/minute",
}


limiter = Limiter(key_func=_get_plan_key, default_limits=[PLAN_LIMITS["free"]])


def get_plan_limits(plan: str = "free") -> list[str]:
    return [PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])]
