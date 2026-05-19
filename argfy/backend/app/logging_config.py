"""
Structured logging para argfy.

Dos modos:
- dev:  human-readable, una linea, con colores opcionales (stderr)
- prod: JSON por linea, Coolify/Loki/Datadog friendly

Wire desde main.py (reemplazando `logging.basicConfig(level=logging.INFO)`):
    from .logging_config import setup_logging
    setup_logging()

Para agregar contexto por request (tenant_id, request_id) sin tocar formatter,
usar `extra=` en el log call:
    logger.info("screener call", extra={"tenant_id": tid, "filters": f})

Los keys de `extra` aparecen como campos top-level en el JSON output.
"""
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

_RESERVED_LOGRECORD_KEYS = {
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName",
    "processName", "process", "message", "asctime", "taskName",
}


class JsonFormatter(logging.Formatter):
    """Formato JSON-line. Un objeto por linea, compatible con Loki/Datadog."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts":      datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level":   record.levelname,
            "logger":  record.name,
            "msg":     record.getMessage(),
            "module":  record.module,
            "line":    record.lineno,
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)

        for k, v in record.__dict__.items():
            if k in _RESERVED_LOGRECORD_KEYS or k.startswith("_"):
                continue
            try:
                json.dumps(v)
                payload[k] = v
            except (TypeError, ValueError):
                payload[k] = repr(v)

        return json.dumps(payload, ensure_ascii=False, default=str)


class DevFormatter(logging.Formatter):
    """Una linea legible. Incluye campos extra entre corchetes si los hay."""

    BASE_FMT = "%(asctime)s %(levelname)-7s %(name)s:%(lineno)d %(message)s"

    def __init__(self) -> None:
        super().__init__(fmt=self.BASE_FMT, datefmt="%H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        extras = {
            k: v for k, v in record.__dict__.items()
            if k not in _RESERVED_LOGRECORD_KEYS and not k.startswith("_")
        }
        if extras:
            tail = " ".join(f"{k}={v!r}" for k, v in extras.items())
            base = f"{base}  [{tail}]"
        return base


def setup_logging(level: str = "INFO", json_output: bool | None = None) -> None:
    """Idempotente: limpia handlers previos antes de configurar.

    json_output:
        None  -> autodetect via settings.ENVIRONMENT (prod=JSON, dev=human)
        True  -> forzar JSON
        False -> forzar human-readable
    """
    if json_output is None:
        try:
            from .config import settings
            json_output = getattr(settings, "ENVIRONMENT", "development") == "production"
        except Exception:
            json_output = False

    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter() if json_output else DevFormatter())
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    for noisy in ("uvicorn.access", "sqlalchemy.engine.Engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
