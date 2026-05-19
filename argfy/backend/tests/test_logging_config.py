"""
Tests para app.logging_config: JsonFormatter, DevFormatter, setup_logging.
"""
import io
import json
import logging

import pytest

from app.logging_config import (
    DevFormatter,
    JsonFormatter,
    setup_logging,
)


def _make_record(
    msg: str = "hello",
    level: int = logging.INFO,
    name: str = "test",
    extra: dict | None = None,
) -> logging.LogRecord:
    record = logging.LogRecord(
        name=name, level=level, pathname="t.py", lineno=42,
        msg=msg, args=(), exc_info=None,
    )
    if extra:
        for k, v in extra.items():
            setattr(record, k, v)
    return record


class TestJsonFormatter:
    def test_basic_fields_present(self):
        f = JsonFormatter()
        out = f.format(_make_record("hi"))
        obj = json.loads(out)
        assert obj["msg"] == "hi"
        assert obj["level"] == "INFO"
        assert obj["logger"] == "test"
        assert obj["line"] == 42
        assert "ts" in obj

    def test_extra_fields_included(self):
        f = JsonFormatter()
        out = f.format(_make_record(extra={"tenant_id": "T1", "duration_ms": 12.3}))
        obj = json.loads(out)
        assert obj["tenant_id"] == "T1"
        assert obj["duration_ms"] == 12.3

    def test_non_serializable_extras_repr_fallback(self):
        class Weird:
            def __repr__(self):
                return "<weird>"

        f = JsonFormatter()
        out = f.format(_make_record(extra={"obj": Weird()}))
        obj = json.loads(out)
        assert obj["obj"] == "<weird>"

    def test_output_is_single_line(self):
        f = JsonFormatter()
        out = f.format(_make_record("multi\nline\nmsg"))
        assert out.count("\n") == 0

    def test_exception_serialized(self):
        try:
            raise ValueError("boom")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
        rec = logging.LogRecord(
            name="t", level=logging.ERROR, pathname="t.py", lineno=1,
            msg="oops", args=(), exc_info=exc_info,
        )
        obj = json.loads(JsonFormatter().format(rec))
        assert "exc" in obj
        assert "ValueError" in obj["exc"]


class TestDevFormatter:
    def test_no_extras_no_brackets(self):
        f = DevFormatter()
        out = f.format(_make_record("plain"))
        assert "plain" in out
        assert "[" not in out.split("plain")[-1]

    def test_extras_appended_in_brackets(self):
        f = DevFormatter()
        out = f.format(_make_record("msg", extra={"tenant_id": "T1"}))
        assert "tenant_id='T1'" in out
        assert out.endswith("]")


class TestSetupLogging:
    def teardown_method(self):
        root = logging.getLogger()
        for h in list(root.handlers):
            root.removeHandler(h)

    def test_setup_is_idempotent(self):
        setup_logging("INFO", json_output=False)
        first_count = len(logging.getLogger().handlers)
        setup_logging("INFO", json_output=False)
        assert len(logging.getLogger().handlers) == first_count

    def test_setup_respects_level(self):
        setup_logging("WARNING", json_output=False)
        assert logging.getLogger().level == logging.WARNING

    def test_setup_json_mode_emits_valid_json(self):
        setup_logging("INFO", json_output=True)
        root = logging.getLogger()
        buf = io.StringIO()
        for h in list(root.handlers):
            root.removeHandler(h)
        handler = logging.StreamHandler(buf)
        handler.setFormatter(JsonFormatter())
        root.addHandler(handler)
        root.setLevel(logging.INFO)

        logging.getLogger("test.app").info("hello", extra={"tenant_id": "X"})
        line = buf.getvalue().strip()
        obj = json.loads(line)
        assert obj["msg"] == "hello"
        assert obj["tenant_id"] == "X"

    def test_noisy_loggers_silenced(self):
        setup_logging("DEBUG", json_output=False)
        assert logging.getLogger("uvicorn.access").level == logging.WARNING
        assert logging.getLogger("sqlalchemy.engine.Engine").level == logging.WARNING
