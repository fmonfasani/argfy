# ── builder: compila deps con toolchain, descartado en imagen final ──
FROM python:3.11-slim AS builder
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt \
 && pip install --user --no-cache-dir gunicorn

# ── runtime: slim sin toolchain, non-root user ──
FROM python:3.11-slim AS runtime
WORKDIR /app

# libpq5 (runtime psycopg2) + curl (healthcheck). NO build-essential.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --system --gid 1001 argfy \
 && useradd  --system --uid 1001 --gid argfy --home /home/argfy --create-home argfy

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    WEB_CONCURRENCY=1 \
    PATH=/home/argfy/.local/bin:$PATH

COPY --from=builder --chown=argfy:argfy /root/.local /home/argfy/.local
COPY --chown=argfy:argfy . .

USER argfy
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD gunicorn app.main:app \
    --workers ${WEB_CONCURRENCY:-1} \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
