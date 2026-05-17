# Plan Argfy — Estado Actual v2.0 (revisado)

**Fecha:** 16/05/2026
**Autor:** claude (revisión sobre el plan v2.0 de opencode)
**Repositorio:** `valuarty/` + `argfy/`

---

## Resumen ejecutivo

El scaffolding está al ~90%. La **funcionalidad monetizable** (rate-limit por plan, feature-gates funcionando, motor de ratios testeado) está más cerca del **70-75%**. Antes de cobrar hay que cerrar 3 bloqueantes y 1 bug latente.

> **Cambio de tono respecto al v2.0 de opencode:** las celdas que mostraban LOC sumadas (`router + service = 427`) se desglosan, y los gaps invisibles (bug en `feature_gate`, except genérico en scheduler) ahora son tickets explícitos.

---

## 📦 Entregable

Este plan se considera **entregado** cuando se cumplen los 5 puntos siguientes. Cualquier item incompleto = plan no entregado.

### 1. Artefactos de código (commiteados a `main`)

**Nuevos archivos:**
- `argfy/backend/scripts/seed_plans.py` — seed idempotente de `PlanFeature`
- `argfy/backend/Dockerfile` — multi-stage Python 3.11
- `argfy/frontend/Dockerfile` — Next.js standalone
- `argfy/deployment/docker-compose.coolify.yml`
- `argfy/deployment/backup.sh`
- `argfy/deployment/hetzner/provision.sh`
- `argfy/deployment/hetzner/README.md`
- `argfy/deployment/coolify/backend.env.example`
- `argfy/deployment/coolify/frontend.env.example`
- `argfy/deployment/coolify/postgres.env.example`
- `argfy/backend/tests/conftest.py`
- `argfy/backend/tests/test_ratios.py`
- `argfy/backend/tests/test_fundamentals.py`
- `argfy/backend/tests/test_auth.py`
- `.github/workflows/test.yml`
- `.github/workflows/deploy.yml`
- `argfy/frontend/src/app/account/billing/page.tsx`
- `argfy/frontend/src/app/account/api-keys/page.tsx`
- `argfy/frontend/src/app/account/team/page.tsx`

**Archivos modificados:**
- `argfy/backend/app/middleware/feature_gate.py` — fix bug (dependency form)
- `argfy/backend/app/middleware/rate_limit_middleware.py` — slowapi real
- `argfy/backend/app/main.py` — Sentry init + request_id + re-raise routers en prod + llamar `seed_plans`
- `argfy/backend/app/scheduler.py` — `except IntegrityError` específico
- `argfy/backend/app/routers/fundamentals.py` — aplicar `Depends(require_feature(...))` en `/price`, `/history`, `/screener`
- `argfy/frontend/next.config.js` — `output: 'standalone'`

**Archivos eliminados:**
- `argfy/render.yaml`
- `argfy/backend/render.yaml`
- `argfy/scripts/fix-vercel-deploy.sh`
- `argfy/scripts/deployment_preparation.py`
- `argfy/scripts/deployment_manager.py`
- Cualquier referencia a `*.vercel.app` y `*.onrender.com` en código y configs

### 2. Infraestructura provisionada

- VPS Hetzner Cloud **CPX21** corriendo Ubuntu 24.04 con IP pública fija.
- Coolify accesible en `http://<ip>:8000` con server `argfy-prod` registrado.
- `provision.sh` ejecutado exitosamente: ufw activo (22/80/443/8000), swap 4GB, fail2ban corriendo, cron `argfy-pgbackup.sh` en `/etc/cron.d/`.
- DNS resolviendo: `argfy.com`, `www.argfy.com`, `api.argfy.com` → IP del VPS (verificable con `dig +short`).
- Certificados TLS Let's Encrypt válidos en los 3 dominios (verificable en SSL Labs ≥ A).

### 3. URLs verificables públicamente

| URL | Respuesta esperada |
|---|---|
| `https://argfy.com` | 200, HTML con home renderizado |
| `https://argfy.com/cedears` | 200, tabla de screener con ≥ 400 filas |
| `https://api.argfy.com/health` | 200, JSON con `status: "healthy"`, `database: "connected"` |
| `https://api.argfy.com/docs` | 200, OpenAPI/Swagger UI |
| `https://api.argfy.com/api/v1/fundamentals/coverage` | 200, JSON con `total > 400` |
| `https://api.argfy.com/api/v1/fundamentals/AAPL` | 200, JSON con ratios AAPL completos |

### 4. Tag git de release

- Tag `v0.1.0-monetizable` apuntando al commit del deploy verde en `main`.
- Release notes en GitHub con: features incluidas, breaking changes (`render.yaml` removido), checklist de aceptación marcado.

### 5. Documentación operacional

- `argfy/deployment/hetzner/README.md` — runbook que cubre:
  - Cómo entrar al VPS por SSH.
  - Cómo ver logs de cada container (`docker logs argfy-backend-1`).
  - Cómo restaurar un backup desde `/backups/postgres/`.
  - Cómo rotar secretos (Coolify UI).
  - Cómo escalar a CPX31 si hace falta (paso por paso).
  - Cómo apagar el scheduler en caso de runaway (`docker exec ... kill`).
- README raíz del repo actualizado: sección "Deployment" apunta a Hetzner/Coolify, **no** a Render/Vercel.

### ✅ Definition of Done

Todos los checkboxes de las secciones [Aceptación global](#-aceptación-global) y [D10 Aceptación deploy](#d10-aceptación-deploy) marcados. Además: tag `v0.1.0-monetizable` empujado a `origin`, release publicado, y al menos **una transacción de prueba con Mercado Pago en sandbox** completada exitosamente (usuario free → checkout pro → webhook llega → `subscription.plan = "pro"` en DB → `/price` deja de devolver 403).

---

## ✅ BACKEND — Estado real verificado

| Componente | Archivo (LOC reales) | Estado |
|---|---|---|
| Fundamentals API — `/screener`, `/coverage`, `/{ticker}`, `/{ticker}/price`, `/{ticker}/history` | [routers/fundamentals.py](argfy/backend/app/routers/fundamentals.py) (295) | ✅ filtros: `country`, `q`, `offset`, `limit`, `sort` |
| Auth — register, login, google, me, refresh, api-keys | [routers/auth.py](argfy/backend/app/routers/auth.py) (282) + `services/auth.py` | ✅ JWT, bcrypt, Google backend-mediated, ApiKey con `key_hash`+`key_prefix` |
| Billing — MP checkout, webhook, portal, cancel | [routers/billing.py](argfy/backend/app/routers/billing.py) (138) + `services/billing.py` | ✅ Mercado Pago. **No hay Stripe**. |
| Admin — overview, users, invitations, api-keys, billing, etl | [routers/admin.py](argfy/backend/app/routers/admin.py) (419) | ✅ Full CRUD + ETL trigger |
| ETL Jobs — refresh_prices / refresh_sec_filings / recalc_ratios / quality_check | [jobs/](argfy/backend/app/jobs/) (4 archivos) | ✅ implementados, ⚠️ sin tests |
| Scheduler — APScheduler + `UNIQUE(job_name, scheduled_for)` en [models.py:389](argfy/backend/app/models.py#L389) | [scheduler.py](argfy/backend/app/scheduler.py) (125) | ✅ funciona, ⚠️ `except Exception` genérico oculta errores |
| Models — Tenant, User, Subscription, Invitation, ApiKey, PlanFeature, ETLRun, FxRate, Company, PriceDaily, RatioQuarterly, etc. | [models.py](argfy/backend/app/models.py) (521) | ✅ |
| Middleware — `auth.py`, `feature_gate.py`, `rate_limit_middleware.py` | [middleware/](argfy/backend/app/middleware/) | ⚠️ rate_limit es stub (11 líneas), ⚠️ feature_gate tiene **bug latente** |

---

## ✅ FRONTEND — Estado real verificado

| Componente | Ruta | Estado |
|---|---|---|
| Home | [app/page.tsx](argfy/frontend/src/app/page.tsx) | ✅ |
| Screener `/cedears` | [components/screener/](argfy/frontend/src/components/screener/) (FilterSidebar, ScreenerTable, RatioCell) | ✅ Range sliders, país, búsqueda, URL sync, sort, paginación server-side |
| Detail `/cedears/[ticker]` | [app/cedears/[byma_ticker]/page.tsx](argfy/frontend/src/app/cedears/[byma_ticker]/page.tsx) + [components/charts/](argfy/frontend/src/components/charts/) | ✅ Error boundaries, skeletons |
| Auth pages — login, register, google callback | [app/auth/](argfy/frontend/src/app/auth/) | ✅ |
| Pricing | [app/pricing/page.tsx](argfy/frontend/src/app/pricing/page.tsx) | ✅ |
| Account — perfil + plan | [app/account/page.tsx](argfy/frontend/src/app/account/page.tsx) | ⚠️ Sólo página general; faltan sub-páginas `/billing`, `/api-keys`, `/team` |
| Admin — overview, billing, api-keys, etl, team | [app/admin/](argfy/frontend/src/app/admin/) | ✅ 5 páginas |
| Lib + hooks | [lib/](argfy/frontend/src/lib/) + [hooks/](argfy/frontend/src/hooks/) | ✅ Zod, apiFetch, TanStack Query |
| Footer con disclaimer CNV | [components/Footer.tsx](argfy/frontend/src/components/Footer.tsx) | ✅ |
| Header + dark mode | [components/Header.tsx](argfy/frontend/src/components/Header.tsx) + ThemeToggle | ✅ |

---

## 🚨 BLOQUEANTES — orden corregido

### B1. Bug latente en `@require_feature` (PRIO 1, antes de B2)

[feature_gate.py:14-50](argfy/backend/app/middleware/feature_gate.py#L14-L50) hace dentro del wrapper:

```python
user = kwargs.get("current_user") or Depends(get_current_user)
db   = kwargs.get("db") or Depends(get_db)
```

`Depends(...)` **no resuelve en runtime** fuera de la firma del endpoint. Si el endpoint no recibe `current_user` y `db` por kwarg con esos nombres exactos, `has_feature` recibe un `Depends`-object y revienta. Es decir, **aplicar `@require_feature` hoy a `/price` o `/history` rompe los endpoints**.

**Fix correcto** — convertir a dependency function en vez de decorator:

```python
# middleware/feature_gate.py
def require_feature(feature_key: str):
    def _check(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        if not has_feature(db, current_user.tenant_id, feature_key):
            raise HTTPException(403, detail={
                "error": "feature_locked",
                "feature": feature_key,
                "upgrade_url": f"/pricing?feature={feature_key}",
            })
        return current_user
    return _check
```

Y en los routers:

```python
@router.get("/{byma_ticker}/price",
    dependencies=[Depends(require_feature("historical_prices"))])
def price_history(...): ...
```

**Aceptación:** test pytest que llama `/price` con tenant free → 403 con `error: feature_locked`.

---

### B2. Rate limiter por plan (PRIO 2)

[rate_limit_middleware.py](argfy/backend/app/middleware/rate_limit_middleware.py) es stub de 11 líneas.

**Implementación recomendada (sin Redis, in-memory):**

- `slowapi` con key derivado de `tenant_id` (de JWT) o `key_prefix` (de API key).
- Limits desde `PLAN_LIMITS = {"free": "10/minute", "pro": "60/minute", "enterprise": "300/minute"}`.
- Si el container escala a >1 worker, in-memory diverge — aceptable para MVP, agregar Redis (Coolify lo deploya con 1 click) cuando haya tráfico real.
- Excluir paths públicos (`/`, `/health`, `/docs`, `/api/v1/auth/*`).

**Aceptación:** test que dispara 11 requests `/screener` con plan free → la 11ª devuelve 429.

---

### B3. Seed `PlanFeature` (PRIO 3)

Sin esto, `has_feature(...)` devuelve `False` siempre → todos los `@require_feature` bloquean a usuarios pro y enterprise.

`scripts/seed_plans.py` debe insertar:

```python
{
  "free":       ["screener_basic"],
  "pro":        ["screener_basic", "historical_prices", "metric_history", "csv_export"],
  "enterprise": ["screener_basic", "historical_prices", "metric_history",
                 "csv_export", "api_access", "team_invitations", "admin_etl_trigger"],
}
```

Llamar desde `lifespan` con `INSERT ... ON CONFLICT DO NOTHING` para que sea idempotente.

**Aceptación:** después de levantar app fresca, `SELECT plan, count(*) FROM plan_features GROUP BY plan` devuelve 3 filas con totales 1, 4, 7.

---

## 🐛 Bugs y gaps detectados que el v2.0 no listaba

### G1. `record_run` traga excepciones genéricas

[scheduler.py:42-46](argfy/backend/app/scheduler.py#L42-L46):

```python
except Exception:
    session.rollback()
    logger.warning(f"Duplicate run skipped for {job_name} today")
    return None
```

Cualquier error de DB (timeout, deadlock, FK violation) se loggea como "duplicate". Cambiar a `except IntegrityError` específicamente y dejar el resto propagarse.

### G2. APScheduler con múltiples workers

`scheduler.py` usa `BackgroundScheduler` in-process. Si Coolify escala a N replicas, cada una crea su propio scheduler → N intentos de insert por job. La `UniqueConstraint` los salva (sólo gana 1), pero genera N-1 warnings espurios.

**Decisión:** en Coolify mantener `replicas=1` para el servicio backend (variable `WEB_CONCURRENCY=1` en el container). Si más adelante hace falta escalar horizontalmente, mover a `SQLAlchemyJobStore` con leader-election.

### G3. `main.py` silencia ImportError de routers

[main.py:74-77](argfy/backend/app/main.py#L74-L77) atrapa `ImportError` y sigue corriendo. En dev OK, en prod oculta bugs. Agregar:

```python
if settings.ENVIRONMENT == "production" and routers_failed:
    raise RuntimeError(f"Failed to load routers in production: {routers_failed}")
```

### G4. Sin tests del motor de ratios

El cálculo de PER, ROE5y, CAGR EPS, FCFonCE vive en `jobs/recalc_ratios.py`. Un cambio inocente puede romper el screener silenciosamente. **Subir tests de ratios a prioridad alta** (no media).

### G5. Sin observabilidad estructurada

`sentry-sdk[fastapi]` está en `requirements.txt` pero no se inicializa. No hay `request_id`, no hay structlog. Para producción con cron y webhooks de MP, esto es prioridad alta, no baja.

### G6. Sin CI/CD

No existe `.github/workflows/` en ningún nivel del repo. Verificado.

### G7. Sin backups documentados

Sin script `pg_dump`, sin retención. Antes del primer cobro real, debería haber al menos backup diario.

---

## 📋 PRIORIZACIÓN — re-ordenada

### Bloqueantes para monetizar

| # | Tarea | Estimación | Archivos |
|---|---|---|---|
| 1 | **Fix bug `@require_feature`** → dependency function | 30 min | [middleware/feature_gate.py](argfy/backend/app/middleware/feature_gate.py) |
| 2 | **Rate limiter por plan** (slowapi + PLAN_LIMITS) | 2 h | [middleware/rate_limit_middleware.py](argfy/backend/app/middleware/rate_limit_middleware.py), [main.py](argfy/backend/app/main.py) |
| 3 | **Seed PlanFeature** idempotente desde lifespan | 1 h | `scripts/seed_plans.py` (nuevo), [main.py](argfy/backend/app/main.py) |
| 4 | **Aplicar `@require_feature`** en `/price`, `/history`, `/screener` (con dependency form, no decorator) | 1 h | [routers/fundamentals.py](argfy/backend/app/routers/fundamentals.py) |

### Calidad mínima antes de tráfico real

| # | Tarea | Estimación | Archivos |
|---|---|---|---|
| 5 | **Tests de ratios** (`test_ratios.py`: PER, ROE5y, CAGR, FCFonCE con fixtures conocidos) | 3 h | `tests/test_ratios.py`, `tests/conftest.py` |
| 6 | **Tests de endpoints críticos** (`/screener`, `/price`, `/history` con auth y feature-gate) | 3 h | `tests/test_fundamentals.py` |
| 7 | **Sentry init** + `request_id` middleware + structlog | 2 h | [main.py](argfy/backend/app/main.py) |
| 8 | **CI/CD** — workflow que corra pytest + ruff + `npm run build` | 2 h | `.github/workflows/test.yml` (nuevo) |
| 9 | **Fix `record_run` `except IntegrityError`** específico | 15 min | [scheduler.py](argfy/backend/app/scheduler.py) |
| 10 | **Fix `main.py` re-raise en producción** si fallan routers | 15 min | [main.py](argfy/backend/app/main.py) |

### UX y producción

| # | Tarea | Estimación | Archivos |
|---|---|---|---|
| 11 | **Account sub-pages**: `/account/billing`, `/account/api-keys`, `/account/team` | 4 h | `frontend/src/app/account/{billing,api-keys,team}/page.tsx` |
| 12 | **Backups Postgres** — `deployment/backup.sh` con `pg_dump` + retención 7 días | 1 h | `deployment/backup.sh` (nuevo) |
| 13 | **Tests E2E Playwright** — checkout flow + screener filter | 4 h | `e2e/screener.spec.ts`, `e2e/checkout.spec.ts` |
| 14 | **Documentar `WEB_CONCURRENCY=1`** + `replicas=1` para el servicio backend | 15 min | README + `deployment/coolify/backend.env` |

---

## 🏗️ Arquitectura (sin cambios respecto al v2.0)

```
valuarty/
├── plan/
│   ├── plan_frontend_16_05_2026_opencode.md           (v1)
│   ├── plan_frontendv2.0_16_05_2026_opencode.md       (v2 — analizado)
│   └── plan_frontendv2.0_16_05_2026_claude.md         ← este archivo
│
└── argfy/
    ├── backend/
    │   ├── app/
    │   │   ├── main.py                    # FastAPI + lifespan + scheduler
    │   │   ├── models.py                  # SQLAlchemy
    │   │   ├── database.py
    │   │   ├── scheduler.py               # APScheduler + ETLRun
    │   │   ├── config/
    │   │   ├── routers/                   # fundamentals, auth, billing, admin
    │   │   ├── services/                  # auth, billing
    │   │   ├── middleware/
    │   │   │   ├── auth.py
    │   │   │   ├── feature_gate.py        # ⚠️ bug: dependency form, no decorator
    │   │   │   └── rate_limit_middleware.py  # ⚠️ stub
    │   │   └── jobs/                      # refresh_prices, refresh_sec_filings, recalc_ratios, quality_check
    │   ├── scripts/
    │   │   ├── load_data_export.py
    │   │   ├── migrate_sqlite_to_pg.py
    │   │   ├── seed_fundamentals.py
    │   │   └── seed_plans.py              # 🆕 a crear (B3)
    │   ├── Dockerfile                     # 🆕 a crear (D1)
    │   └── tests/
    │       ├── test_main.py               # único existente
    │       ├── conftest.py                # 🆕
    │       ├── test_ratios.py             # 🆕
    │       ├── test_fundamentals.py       # 🆕
    │       └── test_auth.py               # 🆕
    │
    ├── frontend/                          # 🆕 Dockerfile a crear (D2)
    │
    └── deployment/
        ├── backup.sh                      # 🆕 pg_dump retención 7 días
        ├── docker-compose.coolify.yml     # 🆕 stack Coolify-ready (D3)
        ├── hetzner/
        │   ├── provision.sh               # 🆕 script provisioning VPS (D4)
        │   └── README.md                  # 🆕 runbook deploy
        └── coolify/
            ├── backend.env.example        # 🆕 vars de entorno backend
            ├── frontend.env.example       # 🆕 vars de entorno frontend
            └── postgres.env.example       # 🆕 vars del Postgres managed
```

---

## 📌 Aceptación global

Para declarar "listo para monetizar":

- [ ] Todos los tests de `tests/` pasan en CI verde.
- [ ] `curl /api/v1/fundamentals/AAPL/price` con JWT de tenant free → **403 `feature_locked`**.
- [ ] `curl` 11 veces `/screener` con JWT free en 1 minuto → la 11ª responde **429**.
- [ ] `SELECT plan, count(*) FROM plan_features GROUP BY plan` devuelve `free:1, pro:4, enterprise:7` después de un reset de DB.
- [ ] Logs del container backend en Coolify muestran `sentry-sdk initialized` al arrancar.
- [ ] `.github/workflows/test.yml` corre verde en cada PR.
- [ ] `pg_dump` automático escribe en bucket/volumen y deja últimas 7 copias.

---

**Estimación total al verde (sin contar deploy):** ~24 h backend + 4 h frontend + 1 h ops = **~30 h hábiles**.
**Estimación deploy a Hetzner + Coolify:** ~6 h adicionales (sección abajo).

---

## 🚀 DEPLOYMENT — Hetzner Cloud + Coolify

**Decisión arquitectónica:** se descartan Render (backend) y Vercel (frontend). El proyecto se deploya 100% en **un único VPS de Hetzner Cloud** orquestado por **Coolify** (ya instalado en el servidor). Razones:

- **Costo plano y predecible**: 1 VPS CX22 ≈ €4-5/mes vs. Vercel/Render que escalan en costo con tráfico y datos.
- **Postgres co-locado**: latencia backend↔DB ~1ms (vs. ~50ms cross-region).
- **Sin vendor lock-in**: docker-compose portable.
- **Coolify maneja**: TLS automático (Let's Encrypt), CI/CD por git webhook, logs, rollback, backups gestionados.

### Topología

```
┌─────────────────────────────────────────────────────────────┐
│  Hetzner Cloud VPS (CPX21: 3 vCPU, 4 GB RAM, 80 GB SSD)     │
│  IP pública: a.b.c.d                                         │
│  OS: Ubuntu 24.04 LTS                                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Coolify (ya instalado, puerto 8000 admin)           │   │
│  │  └─ Traefik (reverse proxy + TLS auto)               │   │
│  │     ├─ argfy-backend  → :8000 internal              │   │
│  │     │   docker image: build desde repo               │   │
│  │     │   dominio: api.argfy.com                       │   │
│  │     ├─ argfy-frontend → :3000 internal              │   │
│  │     │   docker image: build desde repo               │   │
│  │     │   dominio: argfy.com, www.argfy.com           │   │
│  │     └─ argfy-postgres → :5432 internal (sin público) │   │
│  │         volume: /var/lib/postgresql/data             │   │
│  │         backups: cron diario → /backups/             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### D1. `backend/Dockerfile` — multi-stage

```dockerfile
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

FROM base AS deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

FROM deps AS runtime
COPY . .
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    WEB_CONCURRENCY=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Notas:**
- `WEB_CONCURRENCY=1` por G2 (scheduler in-process).
- `HEALTHCHECK` permite a Coolify hacer rolling deploy seguro.
- Sin migraciones automáticas en build: el `lifespan` corre `Base.metadata.create_all` + seed de planes.

### D2. `frontend/Dockerfile` — Next.js standalone

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN corepack enable && pnpm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000
RUN addgroup --system --gid 1001 nodejs \
 && adduser --system --uid 1001 nextjs
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
```

**Requiere** en `frontend/next.config.js`:
```js
module.exports = { output: 'standalone' }
```

### D3. `deployment/docker-compose.coolify.yml`

Coolify acepta docker-compose directamente. Este es el stack completo:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB:       ${POSTGRES_DB}
      POSTGRES_USER:     ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - argfy_pgdata:/var/lib/postgresql/data
      - ../backend/db/schema.sql:/docker-entrypoint-initdb.d/01_schema.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 3s
      retries: 5
    # Sin `ports:` — sólo accesible dentro de la red de Coolify.

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      ENVIRONMENT: production
      DEBUG: "false"
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET: ${JWT_SECRET}
      CORS_ORIGINS: '["https://argfy.com","https://www.argfy.com"]'
      MP_ACCESS_TOKEN: ${MP_ACCESS_TOKEN}
      MP_WEBHOOK_SECRET: ${MP_WEBHOOK_SECRET}
      GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID}
      GOOGLE_CLIENT_SECRET: ${GOOGLE_CLIENT_SECRET}
      SENTRY_DSN: ${SENTRY_DSN}
      WEB_CONCURRENCY: "1"
      ENABLE_SCHEDULER: "true"
      TZ: UTC
    depends_on:
      postgres:
        condition: service_healthy
    labels:
      - "coolify.managed=true"
      - "traefik.enable=true"
      - "traefik.http.routers.argfy-backend.rule=Host(`api.argfy.com`)"
      - "traefik.http.routers.argfy-backend.tls.certresolver=letsencrypt"
      - "traefik.http.services.argfy-backend.loadbalancer.server.port=8000"

  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      NEXT_PUBLIC_API_BASE: https://api.argfy.com/api/v1
      NEXT_PUBLIC_BACKEND_URL: https://api.argfy.com
      NEXT_PUBLIC_GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID}
    depends_on:
      - backend
    labels:
      - "coolify.managed=true"
      - "traefik.enable=true"
      - "traefik.http.routers.argfy-frontend.rule=Host(`argfy.com`) || Host(`www.argfy.com`)"
      - "traefik.http.routers.argfy-frontend.tls.certresolver=letsencrypt"
      - "traefik.http.services.argfy-frontend.loadbalancer.server.port=3000"

volumes:
  argfy_pgdata:
    name: argfy_pgdata
```

### D4. `deployment/hetzner/provision.sh` — script de provisioning

Asume un VPS fresh con Ubuntu 24.04 y acceso root via SSH. **Coolify ya está instalado**, así que este script sólo prepara el resto: hardening básico, swap, firewall, backups y carpetas para Coolify.

```bash
#!/usr/bin/env bash
# Provisioning Hetzner VPS para argfy
# Uso: ssh root@<IP> 'bash -s' < provision.sh
set -euo pipefail

# ── 0. Sanity ─────────────────────────────────────────────
[[ $EUID -ne 0 ]] && { echo "Run as root"; exit 1; }
. /etc/os-release
[[ "$VERSION_ID" != "24.04" ]] && echo "Warning: tested on Ubuntu 24.04, got $VERSION_ID"

# ── 1. Update + paquetes base ─────────────────────────────
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -y upgrade
apt-get -y install \
    ufw fail2ban unattended-upgrades \
    curl wget git jq htop ncdu vim tmux \
    ca-certificates gnupg lsb-release \
    postgresql-client-16

# ── 2. Timezone UTC ───────────────────────────────────────
timedatectl set-timezone UTC

# ── 3. Swap (4 GB) — Postgres + builds Next.js consumen ──
if [[ ! -f /swapfile ]]; then
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    sysctl vm.swappiness=10
    echo 'vm.swappiness=10' > /etc/sysctl.d/99-swappiness.conf
fi

# ── 4. Hardening SSH ──────────────────────────────────────
SSHD=/etc/ssh/sshd_config
sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin prohibit-password/' $SSHD
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/'   $SSHD
sed -i 's/^#\?PubkeyAuthentication.*/PubkeyAuthentication yes/'      $SSHD
systemctl reload ssh

# ── 5. Firewall (ufw) ─────────────────────────────────────
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp          # SSH
ufw allow 80/tcp          # HTTP (Traefik → redirige a HTTPS)
ufw allow 443/tcp         # HTTPS
ufw allow 8000/tcp        # Coolify admin (TODO: restringir a tu IP)
ufw --force enable

# ── 6. fail2ban (default jail para SSH) ───────────────────
systemctl enable --now fail2ban

# ── 7. Unattended upgrades para parches de seguridad ─────
dpkg-reconfigure -f noninteractive unattended-upgrades

# ── 8. Verificar Docker (Coolify lo instala) ─────────────
if ! command -v docker &>/dev/null; then
    echo "ERROR: Docker no está instalado. ¿Coolify está realmente instalado?"
    exit 1
fi

# ── 9. Carpetas para Coolify backups ──────────────────────
mkdir -p /backups/postgres
chown root:root /backups
chmod 700 /backups

# ── 10. Cron pg_dump diario (06:00 UTC) ───────────────────
cat > /usr/local/bin/argfy-pgbackup.sh <<'BACKUP'
#!/usr/bin/env bash
set -euo pipefail
TS=$(date -u +%Y%m%d_%H%M%S)
OUT=/backups/postgres/argfy_${TS}.sql.gz
# El container postgres se llama "<stack>-postgres-1" en Coolify, ajustar:
CONTAINER=$(docker ps --format '{{.Names}}' | grep -E 'argfy.*postgres' | head -1)
[[ -z "$CONTAINER" ]] && { echo "No postgres container found"; exit 1; }
docker exec "$CONTAINER" pg_dump -U argfy -d argfy | gzip > "$OUT"
# Retención: 7 días
find /backups/postgres -name "argfy_*.sql.gz" -mtime +7 -delete
echo "[$(date -u +%FT%TZ)] Backup OK: $OUT ($(du -h "$OUT" | cut -f1))"
BACKUP
chmod +x /usr/local/bin/argfy-pgbackup.sh

cat > /etc/cron.d/argfy-backup <<'CRON'
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
0 6 * * * root /usr/local/bin/argfy-pgbackup.sh >> /var/log/argfy-backup.log 2>&1
CRON

# ── 11. Resumen ───────────────────────────────────────────
echo ""
echo "✅ VPS provisionado."
echo ""
echo "   Coolify admin:  http://$(curl -s ifconfig.me):8000"
echo "   Firewall:       ufw status"
echo "   Swap:           $(free -h | grep Swap)"
echo "   Backups cron:   0 6 * * * → /backups/postgres/"
echo ""
echo "Próximos pasos:"
echo "  1) En Coolify UI: agregar este servidor como destino."
echo "  2) Crear Project 'argfy' + Application desde el repo git."
echo "  3) Pegar deployment/docker-compose.coolify.yml como compose stack."
echo "  4) Setear envs desde deployment/coolify/*.env.example."
echo "  5) Apuntar argfy.com, www.argfy.com, api.argfy.com → IP del VPS."
echo "  6) Deploy."
```

### D5. `deployment/coolify/*.env.example` — variables que el operador llena en Coolify UI

**`backend.env.example`:**
```bash
# Database
POSTGRES_DB=argfy
POSTGRES_USER=argfy
POSTGRES_PASSWORD=<generar con `openssl rand -base64 32`>

# Auth
SECRET_KEY=<openssl rand -hex 32>
JWT_SECRET=<openssl rand -hex 32>

# Mercado Pago (prod)
MP_ACCESS_TOKEN=APP_USR-xxxx
MP_WEBHOOK_SECRET=<openssl rand -hex 24>

# Google OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxx

# Observability
SENTRY_DSN=https://xxx@sentry.io/xxx
```

**`frontend.env.example`:**
```bash
NEXT_PUBLIC_API_BASE=https://api.argfy.com/api/v1
NEXT_PUBLIC_BACKEND_URL=https://api.argfy.com
NEXT_PUBLIC_GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
```

### D6. CI/CD — auto-deploy desde GitHub vía webhook de Coolify

Coolify expone un webhook por aplicación. Configuración:

1. En Coolify UI, "Webhooks" → copiar la URL secreta.
2. GitHub repo → Settings → Webhooks → agregar la URL, evento `push` en `main`.
3. Cada push a `main` → Coolify pulla el repo, builda los Dockerfiles, hace rolling deploy.

**Alternativa con GitHub Actions** (más control + tests previos):

```yaml
# .github/workflows/deploy.yml
name: Deploy to Hetzner via Coolify
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r argfy/backend/requirements.txt
      - run: cd argfy/backend && pytest -q
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Coolify deploy
        run: |
          curl -X POST "${{ secrets.COOLIFY_WEBHOOK_URL }}" \
               -H "Authorization: Bearer ${{ secrets.COOLIFY_WEBHOOK_TOKEN }}"
```

### D7. DNS — registros a crear

| Tipo | Host | Valor | Notas |
|---|---|---|---|
| A | `argfy.com` | `<IP del VPS>` | apex |
| A | `www.argfy.com` | `<IP del VPS>` | |
| A | `api.argfy.com` | `<IP del VPS>` | backend |
| CAA | `argfy.com` | `0 issue "letsencrypt.org"` | seguridad TLS |

Traefik (dentro de Coolify) gestiona los certificados Let's Encrypt automáticamente — sin acción manual.

### D8. Runbook deploy inicial (orden estricto)

| Paso | Acción | Tiempo |
|---|---|---|
| 1 | Crear VPS CPX21 en Hetzner Cloud (ya hay Coolify instalado) | 5 min |
| 2 | `scp provision.sh root@<ip>:/tmp/ && ssh root@<ip> bash /tmp/provision.sh` | 10 min |
| 3 | Configurar DNS según D7 (esperar propagación con `dig`) | 10 min |
| 4 | En Coolify UI: nuevo Project → "argfy" → conectar repo git | 5 min |
| 5 | Pegar `deployment/docker-compose.coolify.yml` como compose stack | 2 min |
| 6 | Llenar envs desde `coolify/*.env.example` | 15 min |
| 7 | Deploy inicial — esperar build de las 3 imágenes | 15-20 min |
| 8 | Smoke test: `curl https://api.argfy.com/health` → 200; `curl https://argfy.com` → 200 | 5 min |
| 9 | Cargar datos: `docker exec argfy-backend python scripts/load_data_export.py` | 10 min |
| 10 | Verificar `/screener` con datos reales | 5 min |
| 11 | Configurar webhook GitHub → Coolify | 5 min |
| 12 | Push a `main` → confirmar auto-deploy verde | 5 min |

**Total deploy inicial:** ~1h30 de reloj.

### D9. Decisiones explícitas (eliminadas del proyecto)

- ❌ **`argfy/render.yaml`** — eliminar.
- ❌ **`argfy/scripts/fix-vercel-deploy.sh`** — eliminar.
- ❌ **`argfy/scripts/deployment_*.py`** (preparation, manager) — auditar y eliminar si son Render/Vercel-specific.
- ❌ **CORS hacia `*.vercel.app`** en `render.yaml` y `.env*` — reemplazar por `argfy.com`/`www.argfy.com`.
- ❌ **`DATABASE_URL=sqlite:///...`** en `render.yaml` — reemplazado por la conexión a Postgres en el compose.

### D10. Aceptación deploy

- [ ] `provision.sh` corrido sin errores; `ufw status` muestra `22, 80, 443, 8000` allow.
- [ ] `curl https://api.argfy.com/health` → 200 con `database: connected`.
- [ ] `curl https://argfy.com/cedears` → HTML con tabla renderizada.
- [ ] Cert TLS válido (`A+` en SSL Labs para ambos dominios).
- [ ] `docker exec ... pg_dump` corre desde el cron y deja archivos en `/backups/postgres/`.
- [ ] Push a `main` → Coolify deploya automáticamente y el commit nuevo aparece en `GET /` con `version`.
- [ ] **No queda en el repo ningún archivo `render.yaml` ni referencia a `*.vercel.app`** (`grep -ri "render\|vercel"` vacío).

### D11. Estimación deploy

| # | Tarea | Tiempo |
|---|---|---|
| D1 | `backend/Dockerfile` multi-stage | 30 min |
| D2 | `frontend/Dockerfile` standalone + ajustar `next.config.js` | 30 min |
| D3 | `docker-compose.coolify.yml` con labels Traefik | 45 min |
| D4 | `provision.sh` + probar en VPS limpio | 1 h |
| D5 | `coolify/*.env.example` + generar secretos prod | 30 min |
| D6 | Webhook GitHub → Coolify + `.github/workflows/deploy.yml` | 45 min |
| D7 | DNS + esperar propagación | 30 min |
| D8 | Deploy inicial + smoke test + carga datos | 1h 30min |
| D9 | Limpieza de archivos Render/Vercel | 30 min |
| **Total** | | **~6 h** |

