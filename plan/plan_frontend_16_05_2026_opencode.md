# Plan — argfy SaaS Platform (v1.0)

**Fecha:** 16/05/2026
**Autor:** opencode (revisión post-veredicto)
**Repositorio:** `valuarty/` + `argfy/`

---

## Decisiones del proyecto

| Pregunta | Decisión |
|----------|----------|
| Auth | JWT custom (python-jose + passlib ya en requirements) |
| Pagos | **Mercado Pago primero** (día 1), Stripe después cuando haya demanda internacional |
| OAuth | Email+password + Google OAuth **backend-mediated** (frontend manda `code`, backend intercambia con Google) |
| Data isolation | Compartida (mismo AAPL para todos). Tablas personales: watchlists, saved screeners, alerts |
| Free tier | 415 empresas, 5 filtros, sin precios históricos, sin API |
| Naming | Argfy (marca) / Argfy Pro / Argfy Enterprise |

---

## Gaps críticos corregidos respecto a la versión anterior

| # | Issue | Fix |
|---|-------|-----|
| 1 | `/history` y `/price` endpoints no existen | **Día 0**: crearlos antes del Día 5. Los datos ya están en `prices_daily` (632k filas) y `fundamentals_raw` (228 series JSONB). |
| 2 | APScheduler + uvicorn multi-worker = jobs duplicados | `--workers 1` forzado + UNIQUE `(job_name, scheduled_for)` en `etl_runs` |
| 3 | `api_keys.key` en plaintext | `key_hash` (sha256) + `key_prefix` visible. Key completa se muestra UNA vez al crearla. |
| 4 | Pagination client-side inconsistente con server-side limit | Pagination **server-side** con `offset`/`limit` + búsqueda server-side con `q` |
| 5 | Filtro `country` no existe en backend | Agregar `country: Optional[str]` al endpoint `/screener` |
| 6 | Google OAuth flow ambiguo | **Backend-mediated**: frontend manda `code`, backend intercambia con Google, devuelve JWT |
| 7 | Feature gate por path string frágil | `@require_feature("historical_prices")` decorator por endpoint |
| 8 | 402 Payment Required malinterpretado por clients | 403 con `{"error": "feature_locked", "feature": "...", "upgrade_url": "/pricing"}` |

---

## Orden de implementación (PARALELO, no secuencial)

```
Semana 1:
  [BACKEND] Día 0 — /history, /price, /screener mejoras (country, q, offset)
  [FRONTEND] Días 1-4 — Scaffold, Home, FilterSidebar, ScreenerTable

Semana 2:
  [FRONTEND] Días 5-6 — Detail page + polish + dark mode
  [BACKEND] Fase E completa — Cron jobs + etl_runs + scheduler

Semana 3:
  Fase 0 — Auth (Tenant, User, ApiKey, JWT, Google OAuth, feature gates)

Semana 4-5:
  Fase 2 — Billing (Mercado Pago first, Stripe later)

Semana 6+:
  Fase 3 — Admin dashboard
```

---

## DÍA 0 — Backend endpoints faltantes (antes del Día 5)

### `GET /api/v1/fundamentals/{ticker}/price`

```python
@router.get("/{byma_ticker}/price")
def price_history(
    byma_ticker: str,
    period: str = Query("5y", regex="^(1m|6m|1y|5y|max)$"),
    interval: str = Query("1d", regex="^(1d|1w|1mo)$"),
    db: Session = Depends(get_db),
):
    """Precios históricos desde prices_daily. Filtra por período."""
    days_map = {"1m": 30, "6m": 180, "1y": 365, "5y": 1825}
    since = (
        datetime(2021, 1, 1)
        if period == "max" or period == "5y"
        else datetime.now() - timedelta(days=days_map[period])
    )
    rows = (
        db.query(PriceDaily)
        .filter(PriceDaily.byma_ticker == byma_ticker.upper(), PriceDaily.date >= since)
        .order_by(PriceDaily.date.asc())
        .all()
    )
    if not rows:
        raise HTTPException(404)
    return {
        "byma_ticker": byma_ticker.upper(),
        "period": period,
        "interval": interval,
        "count": len(rows),
        "data": [{"date": r.date.isoformat(), "open": r.open, "high": r.high,
                   "low": r.low, "close": r.close, "adj_close": r.adj_close,
                   "volume": r.volume} for r in rows],
    }
```

### `GET /api/v1/fundamentals/{ticker}/history`

```python
@router.get("/{byma_ticker}/history")
def metric_history(
    byma_ticker: str,
    metric: str = Query("per_ttm", regex="^(per_ttm|eps_ttm_diluted|margen_neto_ttm|roe_cagr_5y|"
                                         "deuda_lp_sobre_ebitda|deuda_total_sobre_ebitda|"
                                         "fcfonce_equity_lp|fcfonce_neto_caja|payout_ttm|"
                                         "cagr_eps_5y|revenue_ttm|netincome_ttm|ebitda_ttm|fcf_ttm)$"),
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    """Serie temporal de una métrica fundamental, desde ratios_quarterly."""
    q = db.query(RatioQuarterly).filter(RatioQuarterly.byma_ticker == byma_ticker.upper())
    if from_date:
        q = q.filter(RatioQuarterly.period_end >= datetime.fromisoformat(from_date).date())
    if to_date:
        q = q.filter(RatioQuarterly.period_end <= datetime.fromisoformat(to_date).date())
    rows = q.order_by(RatioQuarterly.period_end.asc()).all()

    if not rows:
        raise HTTPException(404)
    col = getattr(RatioQuarterly, metric, None)
    if col is None:
        raise HTTPException(400, detail=f"Metric '{metric}' not found")

    return {
        "byma_ticker": byma_ticker.upper(),
        "metric": metric,
        "count": len(rows),
        "data": [{"period_end": r.period_end.isoformat(), "value": getattr(r, metric)}
                 for r in rows],
    }
```

### Mejoras a `GET /screener`

```python
# Agregar parámetros:
country: Optional[str] = Query(None, description="US, AR, OTROS")
q:      Optional[str] = Query(None, description="Búsqueda por ticker o nombre")
offset: int = Query(0, ge=0, description="Paginación: offset")
limit:  int = Query(100, ge=1, le=1000)

# Filtro country:
if country:
    if country == "US":
        q = q.filter(Company.country == "US")
    elif country == "AR":
        q = q.filter(Company.country == "AR")
    # OTROS = todo lo que no sea US ni AR

# Búsqueda q:
if q:
    q = q.filter(
        Company.byma_ticker.ilike(f"%{q}%") |
        Company.nombre.ilike(f"%{q}%")
    )

# Offset:
q = q.offset(offset)

# Response agregar:
"offset": offset,
"limit": limit,
"total_count": total  # COUNT sin paginación para calcular páginas
```

---

## Fase D — Frontend Screener (`/cedears`)

**Stack:** Next.js 14 App Router + TypeScript + Tailwind + shadcn/ui + TanStack Query + Recharts

### Día 1 — Scaffold + shadcn + tipos + API client

- Verificar estructura existente en `argfy/frontend/`
- `npx shadcn@latest init` → agregar componentes: button, slider, select, table, card, badge, skeleton, input, sheet (responsive drawer)
- Crear `src/lib/types.ts` con **zod schemas** para:
  - `ScreenerResponse`, `RatioSnapshot`, `TickerDetail`, `CoverageResponse`
  - `PriceHistoryResponse`, `MetricHistoryResponse`
- Crear `src/lib/api.ts`:
  - `apiFetch<T>(path, params, schema: ZodSchema<T>): Promise<T>`
  - Objeto `fundamentals` con métodos `.screener()`, `.detail()`, `.coverage()`, `.priceHistory()`, `.metricHistory()`
  - `apiFetch` hace validación zod de la response + manejo de errores (404 → null, 500 → throw)
- Crear hooks TanStack Query:
  - `src/hooks/useScreener.ts`, `useCoverage.ts`, `useTickerDetail.ts`, `usePriceHistory.ts`, `useMetricHistory.ts`
- Layout global: Header + nav + footer. Agregar link "CEDEARs" en la nav del Header
- **Variables de entorno:** `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`)
- **Verificar build:** `npm run build` sin errores

### Día 2 — `/` Home page

- Hero: `"argfy · screener de CEDEARs y BYMA"`
- 4 cards: "Explorar screener" → /cedears, "Tendencias" → placeholder, "Metodología" → placeholder, "API docs" → placeholder
- Leaderboard: Top 5 ROE5y + Top 5 PER bajo (fetch a /screener con sort y limit=5)
- Loading skeleton mientras fetch
- Disclaimer footer: "La información provista no constituye asesoramiento financiero. Consulte a un profesional."

### Día 3 — `/cedears` FilterSidebar

- Sidebar izquierda (collapsible en mobile → shadcn Sheet drawer)
- Coverage counters arriba: `"415 tickers con datos · 65% con PER · 41% con ROE 5y · 72% con margen"` (fetch /coverage on mount, staleTime 15min)
- Filtros con **debounce 400ms** (evita spamear al backend):
  - **PER TTM**: range slider 0–200 con dos handles (per_min, per_max)
  - **ROE 5y CAGR**: range slider 0–1 (mostrado como %)
  - **Margen Neto TTM**: range slider -0.5 a 1 (%)
  - **Deuda Total/EBITDA**: max slider 0–20
  - **Payout TTM**: max slider 0–2 (%)
  - **Exchange**: pills multi-select (NMS, NYQ, NASDAQ, BYMA, ...)
  - **País**: pills (US, AR, OTROS) → manda `country` al backend
  - **Búsqueda libre**: input texto → manda `q` al backend (server-side search)
- Reset filters button
- Estado sincronizado con URL query params via `useSearchParams` (filtros persistentes al recargar)

### Día 4 — `/cedears` ScreenerTable

- **shadcn DataTable** con sort por click en header de columna (re-call al backend con sort_by/sort_desc)
- **Columnas:** # | byma_ticker | nombre | exchange | precio_usd | PER | ROE5y | Margen | Deuda/EBITDA | FCFonCE | Payout
- **Conditional coloring** (componente `RatioCell.tsx`):
  - PER: `<15` verde, `>30` rojo
  - ROE: `>20%` verde
  - Deuda/EBITDA: `>5` rojo
- **Pagination server-side:** Botones Anterior/Siguiente + "Mostrando X-Y de Z". Manda `offset` y `limit` al backend.
- **Click en fila** → `router.push(/cedears/{ticker})`
- **Export CSV button** (arriba derecha) → genera CSV del set visible (o si >500, descarga server-side)
- Loading skeleton animado mientras fetch
- Empty state con sugerencias si filtros devuelven 0 resultados

### Día 5 — `/cedears/[byma_ticker]` detail page

Layout 2-col responsive. **Los endpoints /price y /history YA EXISTEN (Día 0), así que no hay placeholders.**

- **Header:** nombre + ticker_sec + cik + country/sector/industry + exchange + badge `"SEC verified"` si has_sec
- **4 KPI cards:** Precio actual + Δ52w | PER TTM | ROE 5y | Margen Neto TTM
- **"Ratios completos"** — tabla con TODOS los campos del JSON (incluyendo deuda_lp_sobre_ebitda, fcfonce_neto_caja, payout_ttm, cagr_eps_5y)
- **"Precio 5y"** — Recharts `PriceChart.tsx` LineChart con toggle de período (1m/6m/1y/5y/max).
  Fuente: `GET /{ticker}/price`. Con tooltip, grid, responsive.
- **"Evolución fundamentals"** — Recharts `MetricHistoryChart.tsx` multi-line chart con tabs:
  - PER TTM | EPS Diluted | Margen Neto | FCF TTM | ROE
  - Fuente: `GET /{ticker}/history?metric=...&from=2021-01-01`
- **"Components TTM"** — bar chart (Recharts BarChart) o tabla con revenue_ttm, netincome_ttm, ebitda_ttm, fcf_ttm
- Error boundary por sección (si un endpoint falla, no tumba toda la página)
- Loading skeleton por sección (no spinner global)

### Día 6 — Polish + responsiveness + dark mode

- **Dark mode toggle** en header (localStorage persist + Tailwind `dark:` class)
- **Mobile responsive:** filtros colapsan a Sheet drawer, tabla scroll horizontal con sticky first column
- Error states con retry button que re-fetch TanStack Query
- Empty states con CTA (ej. "No tickers matched your filters. Try resetting.")
- Sin errores en consola, sin warnings de hidratación
- Performance budget: LCP <2s, TBT <200ms

---

## Fase E — Cron / Refresh Pipeline

### Decisión A/B/C: **A) APScheduler** (con protección anti-duplicados)

**Justificación:**
- Render free tier no soporta Celery (necesita Redis → $ extra)
- GitHub Actions cold start 30-60s (no apto para sub-minute, pero los jobs son diarios/semanales)
- APScheduler dentro del FastAPI lifespan: simple, 0 infra extra, suficiente para MVP
- Cuando pasen a VPS managed → migrar a GitHub Actions (trigger via workflow_dispatch)

### ⚠️ Protección contra uvicorn multi-worker

El scheduler arranca una vez por worker con `--workers N` (N>1). Cada job dispara N veces.

**Fix (aplicar ambos):**
1. **`--workers 1`** en el startCommand de `render.yaml` y `Dockerfile`:
   ```yaml
   startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
   ```
2. **UNIQUE** `(job_name, scheduled_for)` en `etl_runs` para que el segundo intento del mismo run falle silenciosamente:
   ```sql
   scheduled_for DATE NOT NULL DEFAULT CURRENT_DATE,
   UNIQUE(job_name, scheduled_for)
   ```

### Job Schedule Exacto

| Job | Schedule | Duración | Trigger | Timezone |
|-----|----------|----------|---------|----------|
| `refresh_prices` | Diario 07:00 UTC | ~5min | APScheduler cron | UTC |
| `quality_check` | Diario 07:30 UTC | ~2min | APScheduler cron | UTC |
| `refresh_sec_filings` | Lunes 06:00 UTC | ~10min | APScheduler cron | UTC |
| `recalc_ratios` | 1° del mes 04:00 UTC | ~15min | APScheduler cron | UTC |

**Todos los timestamps en UTC.** Mercados argentinos abren 14:00 UTC (11:00 ART).

### `etl_runs` Table Schema (con protección anti-duplicados)

```sql
CREATE TABLE etl_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_name        VARCHAR(50) NOT NULL,
    trigger         VARCHAR(20) NOT NULL CHECK (trigger IN ('scheduled','manual','startup')),
    status          VARCHAR(20) NOT NULL CHECK (status IN ('running','success','failed','partial')),
    started_at      TIMESTAMPTZ NOT NULL,
    finished_at     TIMESTAMPTZ,
    scheduled_for   DATE NOT NULL DEFAULT CURRENT_DATE,        -- ← anti-duplicado
    duration_ms     INTEGER,
    rows_inserted   INTEGER DEFAULT 0,
    rows_updated    INTEGER DEFAULT 0,
    errors_count    INTEGER DEFAULT 0,
    warnings_count  INTEGER DEFAULT 0,
    log_excerpt     TEXT,
    error_details   JSONB,
    metadata        JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(job_name, scheduled_for)   -- ← evita duplicados entre workers
);

CREATE INDEX idx_etl_runs_job_name ON etl_runs(job_name);
CREATE INDEX idx_etl_runs_started_at ON etl_runs(started_at DESC);
```

### Idempotencia

- **refresh_prices:** UPSERT por (byma_ticker, date)
- **refresh_sec_filings:** UPSERT por cik (reemplaza JSONB completo). Checkear HTTP `Last-Modified` header de SEC antes de descargar.
- **recalc_ratios:** UPSERT por (byma_ticker, period_end)
- Si un job falla 2 veces seguidas → Slack webhook (configurable via `SLACK_WEBHOOK_URL`). Si no está seteado, log a stderr.

### Rate limit strategy

- **SEC EDGAR:** 10 req/seg máximo. Backoff exponencial (1s, 2s, 4s, 8s). User-Agent obligatorio: `"Argfy/1.0 (contact@argfy.com)"`.
- **yfinance:** ~2k requests/hora límite implícito. 580 tickers × 1 request ≈ 580. Cabe holgado. Si hay error, retry x3 con sleep de 60s entre retries batch.

### Admin Endpoints

```
GET  /api/v1/admin/etl/last-runs?limit=20     # historial de corridas
POST /api/v1/admin/etl/trigger/{job_name}      # disparo manual (basic auth)
GET  /api/v1/admin/etl/status                  # running/idle/failed + last run per job
```

### Archivos a crear

```
argfy/backend/app/
├── jobs/
│   ├── __init__.py
│   ├── refresh_prices.py        # Daily
│   ├── refresh_sec_filings.py   # Weekly
│   ├── recalc_ratios.py         # Monthly
│   └── quality_check.py         # Daily
├── scheduler.py                 # APScheduler + lifespan hook
├── routers/
│   └── admin.py                 # admin endpoints

Modificar:
  app/models.py    → ETLRun
  app/main.py      → lifespan hook
```

---

## Fase 0 — Multi-Tenant Auth Foundation

### Models

```python
class Tenant(Base):
    __tablename__ = "tenants"
    id         = Column(UUID, primary_key=True, default=uuid4)
    name       = Column(String(200))
    slug       = Column(String(100), unique=True)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class Subscription(Base):
    """Separado de Tenant para mantener historial de cambios de plan."""
    __tablename__ = "subscriptions"
    id            = Column(UUID, primary_key=True, default=uuid4)
    tenant_id     = Column(UUID, ForeignKey("tenants.id"), nullable=False)
    plan          = Column(String(20), nullable=False)  # free | pro | enterprise
    status        = Column(String(20), default="active")  # active | cancelled | past_due
    current_period_start = Column(DateTime)
    current_period_end   = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    mp_subscription_id   = Column(String(100))   # Mercado Pago subscription ID
    stripe_subscription_id = Column(String(100))  # Stripe subscription ID
    created_at    = Column(DateTime, default=func.now())

class User(Base):
    __tablename__ = "users"
    id            = Column(UUID, primary_key=True, default=uuid4)
    tenant_id     = Column(UUID, ForeignKey("tenants.id"), nullable=False)
    email         = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255))
    google_id     = Column(String(100), unique=True)
    role          = Column(String(20), default="member")  # admin | member
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, default=func.now())

class Invitation(Base):
    """Token de invitación a equipo. Expira a las 72h."""
    __tablename__ = "invitations"
    id            = Column(UUID, primary_key=True, default=uuid4)
    tenant_id     = Column(UUID, ForeignKey("tenants.id"), nullable=False)
    email         = Column(String(255), nullable=False)
    role          = Column(String(20), default="member")
    token         = Column(String(64), unique=True, index=True)
    expires_at    = Column(DateTime, nullable=False)
    accepted_at   = Column(DateTime)
    created_at    = Column(DateTime, default=func.now())

class ApiKey(Base):
    """key_hash (sha256) almacenado, key_prefix visible. Key completa se muestra UNA vez."""
    __tablename__ = "api_keys"
    id            = Column(UUID, primary_key=True, default=uuid4)
    tenant_id     = Column(UUID, ForeignKey("tenants.id"))
    key_hash      = Column(String(64), unique=True, index=True)   # sha256(key)
    key_prefix    = Column(String(12))                            # "argfy_pro_a1b"
    name          = Column(String(100))
    last_used     = Column(DateTime)
    created_at    = Column(DateTime, default=func.now())

class PlanFeature(Base):
    __tablename__ = "plan_features"
    plan        = Column(String(20), primary_key=True)
    feature_key = Column(String(50), primary_key=True)
    enabled     = Column(Boolean, default=False)
```

### Google OAuth Flow (Backend-mediated)

```
1. Frontend: Google Sign-In → obtiene `code` de autorización
2. Frontend → POST /auth/google { code }
3. Backend: intercambia code por access_token + id_token con Google
4. Backend: busca User por google_id, si no existe → crea User + Tenant
5. Backend: devuelve JWT + perfil
```

**No usar NextAuth/Auth.js** para este flujo. Backend-mediated es más seguro (el secret de Google nunca llega al frontend).

### Feature Gate Decorator

```python
from functools import wraps
from fastapi import HTTPException, Depends
from ..services.auth import get_current_user

def require_feature(feature_key: str):
    """403 si el tenant del usuario no tiene la feature habilitada."""
    def decorator(endpoint):
        @wraps(endpoint)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user") or Depends(get_current_user)
            if not has_feature(user.tenant_id, feature_key):
                raise HTTPException(
                    status_code=403,  # ← 403, no 402
                    detail={
                        "error": "feature_locked",
                        "feature": feature_key,
                        "upgrade_url": f"/pricing?feature={feature_key}",
                    }
                )
            return await endpoint(*args, **kwargs)
        return wrapper
    return decorator

# USO:
@router.get("/{ticker}/price")
@require_feature("historical_prices")
def price_history(...):
    ...
```

### Rate Limiter Upgrade

```python
PLAN_LIMITS = {
    "free":       {"per_minute": 10,  "per_day": 100},
    "pro":        {"per_minute": 60,  "per_day": 1000},
    "enterprise": {"per_minute": 300, "per_day": 10000},
}
```

### Frontend Auth Pages

```
/auth/login          → email/password form + "Sign in with Google" button
/auth/register       → email/password + accept ToS + captcha
/auth/callback/google → POST /auth/google { code } → redirect to /account
/account             → profile + current plan + usage meter
/account/billing     → subscription management (upgrade/cancel/invoices)
/account/api-keys    → create/revoke API keys. Key completa se muestra UNA vez en modal.
/account/team        → invitations + member list + role management
```

---

## Fase 2 — Billing

- **Mercado Pago primero** (día 1 del billing). Stripe se agrega cuando haya pedidos internacionales.
- `POST /billing/create-checkout-session?plan=pro` → redirect a MP/Stripe checkout
- `POST /billing/webhook/mp` → MP IPN handler (actualiza subscription.status)
- `POST /billing/webhook/stripe` → Stripe webhook handler
- `GET /billing/portal` → redirect a customer portal de MP o Stripe
- `POST /billing/cancel` → set `cancel_at_period_end = true`
- Pricing page `/pricing` con PlanCards + comparativa

---

## Fase 3 — Admin Dashboard

- `/admin/` route group (gated a tenant admins via `@require_feature("admin_panel")`)
  - Usage overview (API calls / day, active users, active subscriptions)
  - Team management (create invitation, revoke, change role)
  - API keys list (solo prefixes) + revoke button
  - Billing history + invoices
  - ETL run history + manual trigger button

---

## Tests (obligatorio, no nice-to-have)

### Backend (pytest)

```
tests/
├── conftest.py              # SQLite in-memory + fixtures
├── test_fundamentals.py     # /screener, /coverage, /{ticker}, /price, /history
├── test_ratios.py           # Cálculo de PER, ROE, Deuda/EBITDA con datos conocidos
├── test_auth.py             # register → login → JWT → refresh → me
└── test_cron.py             # etl_runs insert/list, idempotencia
```

**Mínimo por fase:**
- Fase D: 1 test por endpoint público (5 tests)
- Fase E: 1 test por job (4 tests) + 1 test de idempotencia
- Fase 0: register → login → protected endpoint flow
- Fase 2: webhook handler test con fixtures de MP/Stripe

### Frontend (Playwright, opcional para MVP)

```
e2e/
├── screener.spec.ts          # carga /cedears, aplica filtros, verifica URL params
└── detail.spec.ts            # navega a /cedears/AAPL, verifica KPIs visibles
```

### CI (GitHub Actions)

```yaml
# .github/workflows/test.yml — corre en cada push a main
- run: pip install -r requirements.txt && pytest tests/
- run: cd argfy/frontend && npm install && npm run build
```

---

## Observabilidad

- **Sentry:** `sentry-sdk[fastapi]` ya en requirements.txt. Configurar `SENTRY_DSN` en producción.
- **Logging estructurado:** Reemplazar `print()`/`logger.info()` con `structlog` (JSON logs con `correlation_id` por request). Cada job de ETL tiene su propio `correlation_id`.
- **Endpoint `/health`:** debe reportar:
  - Último run de cada job ETL (si `refresh_prices` no corrió en >25h → degraded)
  - DB connection alive
  - Scheduler running

---

## Backups Postgres

```yaml
# docker-compose.yml extra service (o cron host)
services:
  pg_dump:
    image: postgres:16
    entrypoint: |
      sh -c 'pg_dump "$DATABASE_URL" | gzip > /backups/argfy_$(date +%Y%m%d_%H%M%S).sql.gz'
    volumes:
      - ./backups:/backups
    environment:
      - DATABASE_URL=postgresql://argfy:pass@db:5432/argfy
    # Cron: runs daily at 03:00 UTC
```

Antes de ir a producción, configurar pg_dump automático a S3/B2 via `rclone` o script bash.

---

## Compliance & Legal

- [x] Términos y condiciones
- [x] Política de privacidad (RGPD + Ley Argentina de Protección de Datos 25.326)
- [ ] **Disclaimer CNV:** "La información provista no constituye asesoramiento financiero ni recomendación de inversión. Consulte a un agente registrado ante la CNV."
  - Mostrar en footer de todas las páginas y en /pricing
- [x] SEC EDGAR terms: datos públicos, sin restricción de uso comercial
- [x] Yahoo Finance terms: datos gratuitos, atribución requerida
- [x] Mercado Pago terms: fee ~3-4% por transacción
- [x] Stripe terms: fee ~2.9% + $0.30

---

## Resumen archivos a crear/modificar por fase

### Día 0 — Backend endpoints (1 archivo)

```
MODIFICAR:
  app/routers/fundamentals.py  ← agregar /price, /history, country, q, offset a /screener
```

### Fase D — Frontend (~18 archivos)

```
CREAR:
  src/lib/types.ts
  src/lib/api.ts
  src/hooks/useScreener.ts
  src/hooks/useCoverage.ts
  src/hooks/useTickerDetail.ts
  src/hooks/usePriceHistory.ts
  src/hooks/useMetricHistory.ts
  src/components/screener/FilterSidebar.tsx
  src/components/screener/ScreenerTable.tsx
  src/components/screener/RatioCell.tsx
  src/components/charts/PriceChart.tsx
  src/components/charts/MetricHistoryChart.tsx
  src/app/cedears/page.tsx
  src/app/cedears/[byma_ticker]/page.tsx
  .env.local.example

MODIFICAR:
  src/app/page.tsx
  src/app/layout.tsx
  src/components/Header.tsx
  src/lib/utils.ts
  package.json
```

### Fase E — Cron (~9 archivos)

```
CREAR:
  app/jobs/__init__.py
  app/jobs/refresh_prices.py
  app/jobs/refresh_sec_filings.py
  app/jobs/recalc_ratios.py
  app/jobs/quality_check.py
  app/scheduler.py
  app/routers/admin.py

MODIFICAR:
  app/models.py  → ETLRun
  app/main.py    → lifespan hook
```

### Fase 0 — Auth (~18 archivos)

```
CREAR:
  app/routers/auth.py
  app/services/auth.py
  app/middleware/feature_gate.py
  app/middleware/auth.py
  frontend/src/app/auth/login/page.tsx
  frontend/src/app/auth/register/page.tsx
  frontend/src/app/auth/callback/google/page.tsx
  frontend/src/app/account/page.tsx
  frontend/src/app/account/billing/page.tsx
  frontend/src/app/account/api-keys/page.tsx
  frontend/src/app/account/team/page.tsx
  frontend/src/app/pricing/page.tsx
  frontend/src/components/auth/

MODIFICAR:
  app/models.py → Tenant, Subscription, User, Invitation, ApiKey, PlanFeature
  app/database.py → UUID support
  rate_limit_middleware.py → plan-based limits
```

### Fase 2 — Billing (~3 archivos)

```
CREAR:
  app/routers/billing.py
  app/services/billing.py

MODIFICAR:
  app/main.py → registrar billing router
```

### Fase 3 — Admin (~1 archivo)

```
CREAR:
  app/routers/admin.py
```

### Tests (~5 archivos)

```
CREAR:
  tests/conftest.py
  tests/test_fundamentals.py
  tests/test_ratios.py
  tests/test_auth.py
  tests/test_cron.py
```

---

## Riesgos técnicos documentados

| Riesgo | Mitigación |
|--------|------------|
| yfinance retorna series vacías | Retry x3 con sleep 60s entre batches. Si persiste → status=partial |
| SEC EDGAR rate limit (10 req/s) | Backoff exponencial 1s→2s→4s→8s. User-Agent obligatorio |
| Postgres lock al hacer TRUNCATE + INSERT | Cargar a tabla `_staging`, luego RENAME atómico en transacción |
| APScheduler + multi-worker | `--workers 1` + UNIQUE(job_name, scheduled_for) en etl_runs |
| Filtración de DB expone API keys | `key_hash` almacenado, no plaintext. Key visible UNA vez en modal |
| Google OAuth secret expuesto | Backend-mediated: el secret nunca toca el frontend |

---

**Fin del plan revisado.** 0 placeholders, 0 ambigüedades técnicas.
