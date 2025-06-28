# Logging middleware implementation# backend/app/middleware/logging_middleware.py
from time import perf_counter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

logger = logging.getLogger("argfy.request")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = perf_counter()
        response = await call_next(request)
        duration = (perf_counter() - start) * 1000

        logger.info(
            "%s %s → %s (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )
        # cabecera opcional
        response.headers["X-Response-Time"] = f"{duration:.1f}ms"
        return response
