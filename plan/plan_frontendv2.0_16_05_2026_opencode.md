# Plan Argfy — Estado Actual v2.0

**Fecha:** 16/05/2026
**Autor:** opencode
**Repositorio:** `valuarty/` + `argfy/`

---

## Resumen

Proyecto completo al ~90%. Todo el código del plan original está implementado. Faltan conectividad fina (rate limiter, feature gates), tests, y algunos features de producción.

---

## ✅ BACKEND — COMPLETO

| Componente | Archivos | Líneas | Estado |
|---|---|---|---|
| **Fundamentals API** — `/screener`, `/coverage`, `/{ticker}`, `/{ticker}/price`, `/{ticker}/history` | `routers/fundamentals.py` | 295 | ✅ Completo con country, q, offset, limit, sort |
| **Auth** — register, login, google, me, refresh, api-keys | `routers/auth.py` + `services/auth.py` | 427 | ✅ JWT, bcrypt, Google OAuth backend-mediated |
| **Billing** — MP checkout, webhook, portal, cancel | `routers/billing.py` + `services/billing.py` | 277 | ✅ Mercado Pago integrado |
| **Admin** — overview, users, invitations, api-keys, billing, etl | `routers/admin.py` | 419 | ✅ Full CRUD + ETL trigger |
| **ETL Jobs** — refresh_prices, refresh_sec_filings, recalc_ratios, quality_check | `jobs/*.py` | 282 | ✅ 4 jobs implementados |
| **Scheduler** — APScheduler con cron y anti-duplicados | `scheduler.py` | 124 | ✅ UNIQUE(job_name, scheduled_for) |
| **Models** — Tenant, User, Subscription, Invitation, ApiKey, PlanFeature, ETLRun, FxRate, Company, PriceDaily, RatioQuarterly, etc. | `models.py` | 522 | ✅ Todos los modelos |
| **Middleware** — auth (JWT/API key), feature_gate decorator, rate_limit | `middleware/*.py` | 115 | ✅ Existen, falta configurar rate_limiter |

---

## ✅ FRONTEND — COMPLETO

| Componente | Archivos | Líneas | Estado |
|---|---|---|---|
| **Home** — Hero, 4 cards, leaderboard, secciones económicas | `app/page.tsx` | 123 | ✅ |
| **Screener** — `/cedears` con FilterSidebar + ScreenerTable | `components/screener/*.tsx` (3 archivos) | 503 | ✅ Range sliders, país, búsqueda, URL sync, sort, pagination server-side |
| **Detail** — `/cedears/[ticker]` con KPI cards, PriceChart, MetricHistoryChart | `app/cedears/[byma_ticker]/page.tsx` + `components/charts/*.tsx` (2 archivos) | 487 | ✅ Error boundaries por sección, loading skeletons |
| **Auth pages** — login, register, google callback | `app/auth/*/page.tsx` (3 archivos) | 224 | ✅ |
| **Pricing** — Plan cards | `app/pricing/page.tsx` | 114 | ✅ |
| **Account** — Perfil + plan | `app/account/page.tsx` | 88 | ✅ (faltan sub-pages: billing, api-keys, team) |
| **Admin** — overview, billing, api-keys, etl, team | `app/admin/*/page.tsx` (5 archivos) | 482 | ✅ |
| **API lib** — Zod schemas, apiFetch, hooks (TanStack Query) | `lib/` + `hooks/` (7 archivos) | 421 | ✅ |
| **Footer** — Disclaimer CNV incluido | `Footer.tsx` | 229 | ✅ |
| **Header** — Nav + dark mode toggle | `Header.tsx` | — | ✅ |

---

## ❌ LO QUE FALTA — PRIORIZADO

### Prioridad Alta (bloqueante para monetizar)

| # | Tarea | Detalle | Archivos |
|---|---|---|---|
| 1 | **Rate limiter por plan** | `RateLimitMiddleware` es un stub vacío. Conectar con `PLAN_LIMITS` (free=10/min, pro=60/min, enterprise=300/min) y registrar en `main.py` | `middleware/rate_limit_middleware.py`, `main.py` |
| 2 | **`@require_feature` en endpoints** | El decorator existe pero no se usa. Agregar `@require_feature("historical_prices")` a `/price` y `/history`, `@require_feature("api_access")` a `/screener` | `routers/fundamentals.py` |
| 3 | **Seed de PlanFeature** | No hay datos default. Crear `seed_plans.py` que inserte qué features tiene cada plan (free/pro/enterprise) | `scripts/seed_plans.py` (nuevo) |

### Prioridad Media (calidad + UX)

| # | Tarea | Detalle | Archivos |
|---|---|---|---|
| 4 | **Tests backend (pytest)** | Solo `test_main.py` existe. Faltan: `conftest.py`, `test_fundamentals.py`, `test_ratios.py`, `test_auth.py`, `test_cron.py` | `tests/` (5 archivos nuevos) |
| 5 | **Account sub-pages** | `/account/billing`, `/account/api-keys`, `/account/team` no existen (solo `/account` general) | `frontend/src/app/account/` (3 páginas nuevas) |
| 6 | **CI/CD (GitHub Actions)** | No hay `.github/workflows/test.yml`. Workflow que corra pytest + npm build | `.github/workflows/test.yml` (nuevo) |

### Prioridad Baja (producción)

| # | Tarea | Detalle | Archivos |
|---|---|---|---|
| 7 | **Sentry** | `sentry-sdk[fastapi]` en requirements pero no configurado | `main.py` |
| 8 | **Backups Postgres** | Script de `pg_dump` automático no existe | `deployment/backup.sh` (nuevo) |
| 9 | **Tests E2E Playwright** | `e2e/screener.spec.ts` y `e2e/detail.spec.ts` no existen | `e2e/` (2 archivos nuevos) |

---

## Arquitectura Actual

```
valuarty/
├── plan/                              # Planes de implementación
│   ├── plan_frontend_16_05_2026_opencode.md
│   └── plan_frontendv2.0_16_05_2026_opencode.md  ← este archivo
│
└── argfy/
    ├── backend/
    │   ├── app/
    │   │   ├── main.py                # FastAPI app + lifespan + scheduler
    │   │   ├── models.py              # Todos los modelos SQLAlchemy
    │   │   ├── database.py            # Engine + SessionLocal
    │   │   ├── scheduler.py           # APScheduler + ETLRun tracking
    │   │   ├── config/
    │   │   ├── routers/
    │   │   │   ├── fundamentals.py    # /screener, /coverage, /{ticker}, /price, /history
    │   │   │   ├── auth.py            # register, login, google, me, refresh, api-keys
    │   │   │   ├── billing.py         # MP checkout, webhook, portal, cancel
    │   │   │   └── admin.py           # overview, users, invitations, api-keys, etl
    │   │   ├── services/
    │   │   │   ├── auth.py            # JWT, password, API key helpers
    │   │   │   └── billing.py         # MP preference, webhook handlers
    │   │   ├── middleware/
    │   │   │   ├── auth.py            # get_current_user (JWT + API key)
    │   │   │   ├── feature_gate.py    # @require_feature decorator
    │   │   │   └── rate_limit_middleware.py  # stub (TODO)
    │   │   └── jobs/
    │   │       ├── refresh_prices.py
    │   │       ├── refresh_sec_filings.py
    │   │       ├── recalc_ratios.py
    │   │       └── quality_check.py
    │   └── tests/
    │       └── test_main.py           # único test existente
    │
    └── frontend/
        └── src/
            ├── app/
            │   ├── page.tsx           # Home
            │   ├── cedears/
            │   │   ├── page.tsx       # Screener table
            │   │   └── [byma_ticker]/
            │   │       └── page.tsx   # Detail page
            │   ├── auth/
            │   │   ├── login/page.tsx
            │   │   ├── register/page.tsx
            │   │   └── callback/google/page.tsx
            │   ├── account/page.tsx   # Perfil (faltan sub-pages)
            │   ├── pricing/page.tsx
            │   └── admin/
            │       ├── page.tsx       # Overview
            │       ├── billing/page.tsx
            │       ├── api-keys/page.tsx
            │       ├── etl/page.tsx
            │       └── team/page.tsx
            ├── components/
            │   ├── screener/          # FilterSidebar, ScreenerTable, RatioCell
            │   ├── charts/            # PriceChart, MetricHistoryChart
            │   ├── Header.tsx
            │   └── Footer.tsx         # Disclaimer CNV incluido
            ├── lib/
            │   ├── types.ts           # Zod schemas
            │   ├── api.ts             # apiFetch + fundamentals object
            │   ├── auth.ts            # Auth helpers
            │   └── admin.ts           # Admin API calls
            └── hooks/
                ├── useScreener.ts
                ├── useCoverage.ts
                ├── useTickerDetail.ts
                ├── usePriceHistory.ts
                ├── useMetricHistory.ts
                ├── useAuth.tsx
                └── useDebounce.ts
```

---

**Fin del plan v2.0 — 90% completo, faltan ~10% para producción.**
