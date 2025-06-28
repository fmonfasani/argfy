# Rate limiting middleware implementation# backend/app/middleware/rate_limit_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # TODO: lógica real
        response: Response = await call_next(request)
        return response

