# ARGFY — PLAN DE REINGENIERÍA INCREMENTAL (RFP v1.0)

---

## SECCIÓN 1 — DIAGNÓSTICO EJECUTIVO

Argfy es una plataforma financiera funcional en producción con backend sólido (FastAPI + PostgreSQL, 19 routers, 16 modelos SQLAlchemy, auth multi-tenant, billing Mercado Pago, 4 jobs ETL) y frontend Next.js 14 App Router con screener funcional de 415+ CEDEARs.

**Calificación general: 6/10**
- Backend: 7.5/10 — sólido pero con duplicación (admin router, schedulers, endpoints legacy)
- Frontend: 4.5/10 — funcional pero desorganizado, visualmente inconsistente, 100% client components
- UX/UI: 3/10 — kitchen sink, sin jerarquía, demasiado ruido visual, homepage con 10 secciones estáticas
- Arquitectura frontend: 3/10 — sin design system, monolito en `components/index.tsx` (450+ líneas mezclando types/hooks/api/utils), dual API client (axios legacy + fetch moderno), sin server components
- Deuda técnica backend: 5/10 — schedulers duplicados (APScheduler + UnifiedScheduler), import roto en `economic_cards.py`, `categories.py` contiene TypeScript no Python
- Potencial de transformación: 9/10 — backend sólido con datos reales SEC/EDGAR, screener funcional, 415+ tickers con ratios. La materia prima está

**Qué funciona bien HOY:**
- Screener con filtros (PER, ROE, margen, deuda, país, exchange) + paginación server-side + export CSV
- Detalle de ticker con precio histórico 5y + métricas fundamentales históricas
- Auth: JWT + Google OAuth + API keys, multi-tenant
- Billing: Mercado Pago checkout, webhook, planes free/pro/enterprise
- Jobs ETL: precios diarios (yfinance), SEC filings semanal, ratios mensual, calidad diaria
- Deploy: Docker + Coolify + GitHub Actions CI/CD + Traefik SSL
- Arquitectura de datos fundamental (Company → PriceDaily → FundamentalRaw → FundamentalQuarterly → RatioQuarterly) robusta

---

## SECCIÓN 2 — PROBLEMAS CRÍTICOS

### BLOQUEANTES DE PRODUCCIÓN (fix inmediato)

| # | Problema | Archivo | Impacto |
|---|---|---|---|
| P1 | `@require_feature` usa `Depends()` fuera de firma de endpoint — rompe cualquier endpoint que lo use | `backend/app/middleware/feature_gate.py` | 🔴 Alto — bloquea monetización |
| P2 | Rate limiter es stub vacío de 11 líneas — no limita nada | `backend/app/middleware/rate_limit_middleware.py` | 🔴 Alto — no se puede diferenciar planes |
| P3 | `seed_plans.py` no corre o no persiste — `has_feature()` siempre False | `backend/app/scripts/seed_plans.py` | 🔴 Alto — todos los gates bloquean a todos |
| P4 | `economic_cards.py` importa `enhanced_economic_service` que no existe — 500 si se invoca | `backend/app/routers/economic_cards.py` | 🟡 Medio — router legacy |
| P5 | `categories.py` contiene sintaxis TypeScript (`export const CATEGORIES`) — no compila en Python | `backend/app/config/categories.py` | 🟡 Medio — no se importa activamente |

### ARQUITECTURA FRONTEND (deuda estructural)

| # | Problema | Ubicación |
|---|---|---|
| P6 | 100% Client Components — cero Server Components, zero streaming, cero Suspense boundaries | `src/app/*/page.tsx` |
| P7 | Monolito `components/index.tsx` — 450+ líneas mezclando types, hooks, API client, utils, config de categorías | `src/components/index.tsx` |
| P8 | Dual API client: axios legacy (`apiClient` en `lib/api.ts`) + fetch+Zod moderno (`fundamentals`) — transición incompleta, el legacy se usa en 6 componentes | `src/lib/api.ts`, componentes dashboard |
| P9 | Import roto: `useBCRAReal.ts` importa `@/lib/config` que no existe | `src/hooks/useBCRAReal.ts` |
| P10 | Sin estado global — todo useState + URL params. Auth en React Context, todo lo demás local. Insostenible para escalar | `src/hooks/useAuth.tsx` |
| P11 | Sin loading/error/empty states en 7 de 8 páginas — solo `/cedears` los tiene | `src/app/*/page.tsx` |
| P12 | `@headlessui/react` instalado pero no importado en ningún lado | `package.json` |
| P13 | Axios no está en `package.json` (dependencia transitiva) — riesgo de rotura silenciosa | `package.json` |
| P14 | Dual ESLint config (`.eslintrc.json` + `eslint.config.mjs`) — pueden conflictuar | raíz frontend |
| P15 | `next.config.js` ignora errores de lint y typescript — deuda oculta | `next.config.js` |

### UX/VISUAL (percepción del producto)

| # | Problema |
|---|---|
| P16 | Homepage tipo kitchen sink — 10 secciones estáticas (Banks, Government, BCRA, Finances, Markets, Economics, News, DailyEconomicData, EconomicDataCards, CedearsLeaderboard) sin jerarquía |
| P17 | 3 marquees en layout + 5 legacy no usados = 8 componentes de marquee para una sola función |
| P18 | SecondaryNav con 10 tabs que no navegan a ningún lado — decorativo puro |
| P19 | Sin tipografía premium — Inter genérica sin escala tipográfica definida |
| P20 | Sin sistema de colores semánticos — Tailwind config solo blue/gray, colores usados ad-hoc |
| P21 | Cards sin diferenciación visual — todas las secciones homepage se ven iguales |
| P22 | Dashboard antiguo (`dashboard/Dashboard.tsx`) mezclado con homepage moderna |

### BACKEND (deuda técnica)

| # | Problema |
|---|---|
| P23 | Admin router duplica endpoints: `/admin/last-runs`, `/admin/status`, `/admin/trigger` = `/admin/etl/last-runs`, etc. |
| P24 | Schedulers duplicados: APScheduler + UnifiedScheduler corren en paralelo |
| P25 | `db/schema.sql` no incluye tablas de auth, billing, ni economic_indicators — schema incompleto |
| P26 | `routers/expanded_indicators.py` + `routers/unified_economic.py` + `routers/data.py` — routers legacy duplicados |
| P27 | `services/dollar_multi_source.py`, `services/http_factory.py`, `services/performance/`, `services/modern/` — no usados |
| P28 | Sin tests para el motor de ratios (PER, ROE5y, CAGR EPS, Deuda/EBITDA) |
| P29 | `sentry-sdk` instalado pero no inicializado correctamente |

---

## SECCIÓN 3 — QUÉ MANTENER SÍ O SÍ

### BACKEND (95% intacto)

| Módulo | Archivos | Razón |
|---|---|---|
| Modelos SQLAlchemy | `models.py` — Company, PriceDaily, FundamentalRaw/Quarterly, RatioQuarterly, FxRate, auth models | Schema productivo, relaciones críticas |
| Router fundamentals | `routers/fundamentals.py` — screener, coverage, detail, price, history | Core del producto |
| Router auth | `routers/auth.py` — register, login, google, me, api-keys | Multi-tenant, JWT, API keys |
| Router billing | `routers/billing.py` — MP checkout, webhook, portal, cancel | Monetización activa |
| Router admin | `routers/admin.py` — team, ETL, billing overview | Operación |
| Router health | `routers/health.py` | Monitoreo |
| Router indicators | `routers/indicators.py` — current, historical, search | Dashboard económico |
| Router system | `routers/system.py` — info, config, scheduler, logs | Sysadmin |
| Router bcra_real | `routers/bcra_real.py` | BCRA en tiempo real |
| Jobs ETL | `jobs/refresh_prices.py`, `refresh_sec_filings.py`, `recalc_ratios.py`, `quality_check.py` | Data pipeline |
| Servicios core | `services/auth.py`, `billing.py`, `bcra_service.py`, `dolar_blue_service.py`, `cache_service.py` | Lógica de negocio |
| Tests existentes | `tests/test_auth.py`, `test_fundamentals.py`, `test_main.py`, `test_ratios.py` | Regresión |
| Config | `config/config.py` — Pydantic Settings | Config centralizada |
| Middleware | `middleware/auth.py` — get_current_user | Auth dependency |

### FRONTEND (70% refactor, 30% mantener)

| Módulo | Archivos | Razón |
|---|---|---|
| Screener page + componentes | `app/cedears/*`, `components/screener/*` | Core del producto, bien diseñado |
| Hook system | `hooks/useScreener.ts`, `useTickerDetail.ts`, `useCoverage.ts`, `usePriceHistory.ts`, `useMetricHistory.ts` | React Query + Zod, moderno |
| API layer moderno | `lib/api.ts` — objeto `fundamentals` con fetch+Zod | Type-safe, validado |
| Auth system | `hooks/useAuth.tsx`, `lib/auth.ts`, `components/Providers.tsx` | Multi-tenant, JWT |
| Route structure | `app/*` — App Router pages existentes | Mantener routing, refactor contenido |
| Dockerfile frontend | `Dockerfile` — multi-stage, standalone | Build productivo funcionando |
| Charts | `components/charts/PriceChart.tsx`, `MetricHistoryChart.tsx` | Recharts, funcionales |

### INFRAESTRUCTURA

| Componente | Razón |
|---|---|
| Docker Compose + Coolify | Deploy funcionando |
| GitHub Actions (test + deploy) | CI/CD activo |
| Dockerfiles (backend + frontend) | Build productivo |
| Traefik config (labels) | SSL + routing |
| Postgres schema | Datos productivos |

---

## SECCIÓN 4 — QUÉ ELIMINAR INMEDIATAMENTE

### FRONTEND — BASURA CONFIRMADA

| Archivo | Líneas | Razón | Riesgo |
|---|---|---|---|
| `components/ArgentinaMarquee.tsx` | ~60 | Reemplazado por 3 marquees actuales | Ninguno |
| `components/GlobalMarquee.tsx` | ~60 | Reemplazado por InternationalMarquee | Ninguno |
| `components/TradingViewMarquee.tsx` | ~80 | No usado, reemplazado | Ninguno |
| `components/CustomArgentinaMarquee.tsx` | ~40 | Reemplazado por ArgentineEconomicMarquee | Ninguno |
| `components/MarqueeControlPanel.tsx` | ~120 | Prototipo no conectado | Ninguno |
| `components/charts/charts/*` (4 archivos) | ~200 | Ruta anidada extraña (charts/charts/), duplica funcionalidad de charts/ | Bajo — revisar imports |
| `components/dashboard/*` (4 archivos) | ~300 | Sistema legacy, no wiring en rutas activas | Bajo |
| `components/modal/IndicatorModal.tsx` | ~150 | Sistema legacy, reemplazable por modal del DS | Bajo |
| `components/ui/LoadingSpinner.tsx` | ~30 | Reemplazar por Skeleton del DS | Bajo |

### FRONTEND — SECCIONES HOMEPAGE ESTÁTICAS (reemplazar por dinámicas)

| Archivo | Problema | Acción |
|---|---|---|
| `BanksSection.tsx` | Datos hardcoded | Eliminar de homepage, mantener código por si se rescata |
| `GovernmentSection.tsx` | Datos hardcoded | Eliminar |
| `BCRASection.tsx` | Datos hardcoded | Eliminar (ya hay BCRA dashboard funcional) |
| `FinancesSection.tsx` | Datos hardcoded | Eliminar |
| `MarketsSection.tsx` | Datos hardcoded | Eliminar |
| `EconomicsSection.tsx` | Datos hardcoded | Eliminar |
| `DailyEconomicData.tsx` | Datos hardcoded | Eliminar |
| `NewsSection.tsx` | API funcional + fallback hardcoded | Mantener pero refactorizar |

### BACKEND — ROUTERS MUERTOS

| Router | Problema | Acción |
|---|---|---|
| `routers/expanded_indicators.py` | Duplica indicators.py + categorías TS | Deprecar → eliminar en Fase 2 |
| `routers/unified_economic.py` | Solo test de librerías HTTP | Eliminar |
| `routers/data.py` | Duplica indicators + cards | Deprecar → eliminar |
| `routers/economic_cards.py` | Import roto (no existe el service) | Eliminar |

### BACKEND — SERVICIOS NO USADOS

| Servicio | Acción |
|---|---|
| `services/dollar_multi_source.py` | Eliminar (cubierto por dolar_blue_service.py) |
| `services/http_factory.py` | Eliminar (no usado) |
| `services/unified_service.py` | Eliminar (no usado) |
| `services/performance/bcra_massive_service.py` | Eliminar (no usado) |
| `services/modern/bcra_httpx_service.py` | Eliminar (no usado) |
| `services/scheduler.py` (UnifiedScheduler) | Eliminar (conflicto con APScheduler) |
| `services/data_processor.py` | Archivo vacío, eliminar |

### BACKEND — OTROS

| Archivo | Acción |
|---|---|
| `config/categories.py` | Es TypeScript, eliminar |
| `main.py.backup` | Backup, eliminar |
| `services/bcra_scheduler.py.backup` | Backup, eliminar |

---

## SECCIÓN 5 — NUEVA VISIÓN DE PRODUCTO

Argfy debe reposicionarse como:

> **"Terminal de análisis fundamental para CEDEARs y acciones BYMA"**

No un portal de noticias económicas argentinas. No un dashboard macro genérico. **Una herramienta profesional de stock screening, research y valuations.**

### CORE PRODUCT (3 pilares, priorizados)

| Pilar | Descripción | Estado actual | Prioridad |
|---|---|---|---|
| **Screener** | Filtrar 415+ CEDEARs por PER, ROE, margen, deuda, payout, país, exchange. Entry point del producto. | ✅ Funcional — refinar UX | P0 |
| **Research** | Detalle por ticker con charts de precio 5y, métricas históricas, ratios TTM, perfil de compañía | ✅ Funcional — mejorar visual | P1 |
| **Watchlists + Portfolios** | Listas personalizadas, seguimiento de holdings, alertas de precio/ratio | ❌ No existe | P2 |

### SECONDARY (mantener, no priorizar)

| Feature | Razón |
|---|---|
| Dashboard económico argentino (dólar, inflación, BCRA) | Útil pero no core — colapsado por defecto |
| API pública para desarrolladores | Roadmap Q3 |
| Pricing / Account / Billing | Necesario para monetización, ya funciona |
| Admin panel (ETL, users, billing) | Operativo, mantener |

### ELIMINAR DEL FOCO

| Feature | Razón |
|---|---|
| Secciones estáticas homepage (Banks, Government, 6 más) | No agregan valor, datos hardcoded desactualizados |
| Marquees redundantes (3+5 legacy) | Ruido visual, reemplazar por 1 configurable |
| SecondaryNav decorativo | 10 tabs que no navegan |
| Páginas sin contenido real | `/news`, `/products`, `/analysis`, `/brokers`, `/communities` no existen como rutas |

---

## SECCIÓN 6 — NUEVA ARQUITECTURA FRONTEND

### PRINCIPIOS

1. **Feature-based architecture** — cada feature tiene su carpeta con componentes, hooks, types
2. **Separation of concerns** — UI vs domain logic vs API calls vs state
3. **Server Components por defecto** — solo `"use client"` cuando es necesario
4. **Design System first** — todo componente nuevo usa tokens y primitives del DS
5. **Zustand para UI state** — TanStack Query para server state

### ÁRBOL OBJETIVO

```
src/
├── app/                                    # App Router
│   ├── layout.tsx                          # Root layout (Server Component)
│   ├── page.tsx                            # Homepage (Server Component con streaming)
│   ├── cedears/
│   │   ├── page.tsx                        # Screener (Client Component)
│   │   └── [byma_ticker]/
│   │       └── page.tsx                    # Ticker detail (Client + Server)
│   ├── dashboard/
│   │   └── page.tsx                        # Economic dashboard (collapsible)
│   ├── pricing/
│   │   └── page.tsx                        # Pricing page
│   ├── auth/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   └── account/
│       ├── page.tsx
│       ├── billing/page.tsx
│       └── api-keys/page.tsx
│
├── components/
│   ├── ui/                                 # Design System primitives
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Table.tsx                       # Table shell (virtualized-ready)
│   │   ├── Skeleton.tsx
│   │   ├── Modal.tsx
│   │   ├── Tabs.tsx
│   │   ├── Tooltip.tsx
│   │   ├── Command.tsx                     # Command palette (⌘K)
│   │   ├── EmptyState.tsx
│   │   ├── ErrorBoundary.tsx
│   │   └── LoadingSpinner.tsx
│   │
│   ├── layout/                             # Layout components
│   │   ├── Header.tsx                      # Minimal header
│   │   ├── Sidebar.tsx                     # Collapsible sidebar
│   │   ├── Footer.tsx
│   │   ├── Providers.tsx                   # TanStack Query + Auth + Theme
│   │   └── MarqueeBar.tsx                  # 1 marquee configurable
│   │
│   ├── screener/                           # Screener feature
│   │   ├── FilterSidebar.tsx
│   │   ├── ScreenerTable.tsx
│   │   ├── RatioCell.tsx
│   │   ├── CoverageStats.tsx
│   │   └── SavedFilters.tsx
│   │
│   ├── research/                           # Ticker detail feature
│   │   ├── TickerHeader.tsx
│   │   ├── KeyMetrics.tsx
│   │   ├── PriceChart.tsx
│   │   ├── MetricHistoryChart.tsx
│   │   ├── FinancialTable.tsx
│   │   └── CompanyProfile.tsx
│   │
│   ├── dashboard/                          # Economic dashboard (secondary)
│   │   ├── DashboardGrid.tsx
│   │   └── MetricCard.tsx
│   │
│   └── shared/                             # Cross-feature shared
│       ├── TickerSearch.tsx
│       └── AuthGuard.tsx
│
├── hooks/                                  # React Query hooks
│   ├── useScreener.ts
│   ├── useTickerDetail.ts
│   ├── useCoverage.ts
│   ├── usePriceHistory.ts
│   ├── useMetricHistory.ts
│   ├── useAuth.ts                          # Reemplazar Context por Zustand
│   ├── useDebounce.ts
│   └── useKeyboard.ts
│
├── stores/                                 # Zustand stores
│   ├── authStore.ts                        # User, token, tenant
│   ├── uiStore.ts                          # Sidebar, theme, command palette
│   └── filterStore.ts                      # Screener filters (persisted)
│
├── lib/
│   ├── api/                                # Unified API layer
│   │   ├── client.ts                       # Fetch wrapper + auth + Zod validation
│   │   ├── fundamentals.ts                 # Screener, detail, price, history
│   │   ├── auth.ts                         # Login, register, google, me, api-keys
│   │   ├── billing.ts                      # MP checkout, portal, cancel
│   │   └── admin.ts                        # Admin endpoints
│   ├── types/
│   │   ├── screener.ts                     # Zod schemas + inferred types
│   │   ├── auth.ts
│   │   └── common.ts
│   ├── utils/
│   │   ├── cn.ts                           # clsx + tailwind-merge
│   │   ├── formatters.ts                   # formatValue, formatChange, etc.
│   │   └── constants.ts                    # CATEGORIES, COLORS, API config
│   └── validations/
│       └── schemas.ts                      # Zod schemas (cliente)
│
├── config/
│   ├── navigation.ts                       # Nav items centralizado
│   └── theme.ts                            # Design tokens constantes
│
└── styles/
    ├── globals.css                          # Tailwind directives + resets
    └── tokens.css                           # CSS custom properties
```

### STATE ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    STATE ARCHITECTURE                        │
├─────────────────┬───────────────────┬───────────────────────┤
│   TanStack Query │    Zustand        │    URL Search Params  │
│   (Server State) │   (Client State)  │    (Persistent UI)    │
├─────────────────┼───────────────────┼───────────────────────┤
│ Screener data   │ authStore:        │ Screener filters:     │
│ Ticker detail   │   user, token      │   per_min, per_max,   │
│ Price history   │   tenant, role     │   roe_min, margen,    │
│ Metric history  │   isAuthenticated  │   deuda, payout,      │
│ Coverage stats  │   logout()         │   exchange, country,  │
│ Auth: me        ├───────────────────┤   q, sort_by, offset  │
│ Billing status  │ uiStore:          │                       │
│ Admin data      │   sidebarOpen     │ Compartible via URL   │
│                 │   theme (D/L)     │ (bookmarkeable)       │
│ Cache:          │   commandPalette  │                       │
│   staleTime     │   mobileMenuOpen  │                       │
│   per query     ├───────────────────┤                       │
│                 │ filterStore:      │                       │
│                 │   savedFilters[]  │                       │
│                 │   (persisted)     │                       │
└─────────────────┴───────────────────┴───────────────────────┘
```

### ROUTING STRATEGY

| Ruta | Componente | Tipo | Auth |
|---|---|---|---|
| `/` | HomePage | Server Component + streaming islands | No |
| `/cedears` | CedearsPage | Client Component (useSearchParams) | No |
| `/cedears/[ticker]` | TickerDetailPage | Server + Client hybrid | No (partial: price history locked) |
| `/dashboard` | DashboardPage | Client Component | No |
| `/pricing` | PricingPage | Server Component | No |
| `/auth/login` | LoginPage | Client Component | No |
| `/auth/register` | RegisterPage | Client Component | No |
| `/account` | AccountPage | Client Component | Sí |
| `/account/billing` | BillingPage | Client Component | Sí |
| `/account/api-keys` | ApiKeysPage | Client Component | Sí (pro+) |

### DECISIONES DE ARQUITECTURA (TRADEOFFS)

| Decisión | Por qué sí | Por qué no |
|---|---|---|
| Zustand sobre Redux Toolkit | Menos boilerplate, stores pequeños, suficiente para UI state | Redux es mejor para estado complejo con middlewares — pero no lo necesitamos |
| Server Components por defecto | -40% JS bundle, mejor LCP, streaming nativo | Requiere refactor de hooks existentes — migrar progresivamente |
| TanStack Query para todo server state | Cache, staleTime, refetch, paginación out of the box | Más librería — pero ya la estamos usando |
| UI state en Zustand, no en Context | Evita re-renders innecesarios, persist middleware | Más boilerplate que Context para estados simples |
| URL search params para filtros | Bookmarkeable, compartible, SSR-ready | Mayor complejidad en parse/sync |
| Feature-based folders sobre capas | Cohesión, fácil eliminar feature, escalable | Puede duplicar types entre features |
| Eliminar axios, solo fetch+Zod | Menos dependencias, tipo-safe, más control | Más código boilerplate para requests |

---

## SECCIÓN 7 — NUEVA ARQUITECTURA BACKEND

### PRINCIPIOS
- **Mantener 95% del código existente** — solo refactorizar deuda explícita
- **No romper contratos API** — los endpoints existentes se mantienen idénticos
- **Unificar schedulers** — quedarse con APScheduler, eliminar UnifiedScheduler
- **Eliminar routers muertos** — deprecar primero con warning, eliminar después

### CAMBIOS CONCRETOS

| Módulo | Acción | Riesgo | Rollback |
|---|---|---|---|
| `middleware/feature_gate.py` | Fix: mover `Depends()` a la firma del endpoint | 🔴 Medio si hay dependencias ocultas | Git revert |
| `middleware/rate_limit_middleware.py` | Implementar slowapi real con límites por plan | 🟡 Bajo — no rompe funcionalidad | Git revert |
| `scripts/seed_plans.py` | Fix: asegurar seed en startup con upsert | 🟡 Bajo | Git revert |
| `routers/economic_cards.py` | Eliminar (import roto) | 🟡 Bajo — no hay consumer conocido | Recuperar de git |
| `routers/expanded_indicators.py` | Eliminar | 🟡 Medio — verificar que ningún frontend lo consume | Deprecar 1 semana antes |
| `routers/unified_economic.py` | Eliminar | 🟡 Bajo — solo test | Recuperar de git |
| `routers/data.py` | Eliminar | 🟡 Medio — check consumers | Deprecar |
| `services/scheduler.py` (UnifiedScheduler) | Eliminar, migrar tasks críticas a APScheduler | 🟡 Medio — verificar que tasks existan en APScheduler | Recuperar |
| `admin.py` — dup endpoints | Limpiar `/admin/last-runs`, `/admin/status`, `/admin/trigger` | 🟡 Bajo — duplicados | Git revert |
| Sentry init | Configurar correctamente en startup | 🟡 Bajo | Comentar línea |

### ÁRBOL BACKEND OBJETIVO (reducido)

```
backend/app/
├── main.py                     # Simplificado, routers limpios
├── database.py                 # Sin cambios
├── models.py                   # Sin cambios
├── scheduler.py                # Solo APScheduler (eliminar UnifiedScheduler)
├── config/
│   ├── __init__.py
│   ├── config.py               # Sin cambios
│   └── indicators_mapping.py   # Mantener
├── middleware/
│   ├── auth.py                 # Sin cambios
│   ├── feature_gate.py         # FIXED
│   ├── rate_limit_middleware.py # IMPLEMENTED
│   └── logging_middleware.py   # Sin cambios
├── routers/
│   ├── fundamentals.py         # CORE — intacto
│   ├── auth.py                 # Mantener
│   ├── billing.py              # Mantener
│   ├── admin.py                # Limpiado (dup removal)
│   ├── health.py               # Mantener
│   ├── indicators.py           # Mantener
│   ├── system.py               # Mantener
│   └── bcra_real.py            # Mantener
├── services/
│   ├── auth.py                 # Mantener
│   ├── billing.py              # Mantener
│   ├── bcra_service.py         # Mantener
│   ├── bcra_expanded_service.py # Mantener
│   ├── dolar_blue_service.py   # Mantener
│   ├── cache_service.py        # Mantener
│   └── integrated_data_service.py # Mantener
├── jobs/
│   ├── refresh_prices.py       # Mantener
│   ├── refresh_sec_filings.py  # Mantener
│   ├── recalc_ratios.py        # Mantener
│   └── quality_check.py        # Mantener
├── utils/
│   └── emoji_log.py            # Mantener
└── scripts/
    ├── seed_plans.py           # FIXED
    └── seed_fundamentals.py    # Mantener
```

---

## SECCIÓN 8 — DESIGN SYSTEM PROPUESTO

### TOKENS (CSS Custom Properties)

```css
/* styles/tokens.css */
:root {
  /* Spacing scale (4px base) */
  --space-1:  4px;
  --space-2:  8px;
  --space-3:  12px;
  --space-4:  16px;
  --space-5:  20px;
  --space-6:  24px;
  --space-8:  32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;

  /* Typography */
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --text-xs:   0.75rem;   /* 12px */
  --text-sm:   0.875rem;  /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg:   1.125rem;  /* 18px */
  --text-xl:   1.25rem;   /* 20px */
  --text-2xl:  1.5rem;    /* 24px */
  --text-3xl:  1.875rem;  /* 30px */
  --text-4xl:  2.25rem;   /* 36px */
  --text-5xl:  3rem;      /* 48px */
  --leading-tight:    1.25;
  --leading-normal:   1.5;
  --leading-relaxed:  1.625;
  --tracking-tight:   -0.025em;
  --tracking-normal:  0;
  --tracking-wide:    0.025em;

  /* Colors — Semantic (Dark first, Light overrides)
     Base: slate palette optimizada para finanzas */
  --color-bg-primary:       #0b1120;  /* Slate más profundo que #0f172a */
  --color-bg-secondary:     #1e293b;
  --color-bg-tertiary:      #334155;
  --color-bg-elevated:      #0f172a;
  --color-surface:          #1e293b;
  --color-surface-hover:    #334155;
  --color-surface-active:   #4755692a;
  
  --color-text-primary:     #f1f5f9;
  --color-text-secondary:   #94a3b8;
  --color-text-tertiary:    #64748b;
  --color-text-muted:       #475569;
  --color-text-link:        #60a5fa;
  
  --color-border:           #334155;
  --color-border-hover:     #475569;
  --color-border-active:    #64748b;
  
  --color-accent:           #f59e0b;  /* amber-500 */
  --color-accent-hover:     #d97706;
  --color-accent-muted:     #fbbf2440;
  --color-accent-text:      #fbbf24;
  
  /* Financial semantic */
  --color-positive:         #22c55e;
  --color-negative:         #ef4444;
  --color-neutral:          #94a3b8;
  --color-positive-bg:     #22c55e10;
  --color-negative-bg:     #ef444410;
  
  /* Status */
  --color-success:          #22c55e;
  --color-warning:          #eab308;
  --color-danger:           #ef4444;
  --color-info:             #3b82f6;
  
  /* Radius */
  --radius-sm:  4px;
  --radius-md:  8px;
  --radius-lg:  12px;
  --radius-xl:  16px;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm:  0 1px 2px 0 rgb(0 0 0 / 0.3);
  --shadow-md:  0 4px 6px -1px rgb(0 0 0 / 0.4);
  --shadow-lg:  0 10px 15px -3px rgb(0 0 0 / 0.4);
  --shadow-xl:  0 20px 25px -5px rgb(0 0 0 / 0.4);
  
  /* Transitions */
  --transition-fast:   150ms ease;
  --transition-normal: 200ms ease;
  --transition-slow:   300ms ease;
}

.light {
  --color-bg-primary:       #f8fafc;
  --color-bg-secondary:     #f1f5f9;
  --color-bg-tertiary:      #e2e8f0;
  --color-surface:          #ffffff;
  --color-surface-hover:    #f1f5f9;
  --color-text-primary:     #0f172a;
  --color-text-secondary:   #475569;
  --color-text-tertiary:    #64748b;
  --color-text-muted:       #94a3b8;
  --color-border:           #e2e8f0;
  --color-border-hover:     #cbd5e1;
  --color-positive:         #16a34a;
  --color-negative:         #dc2626;
}
```

### TAILWIND EXTEND

```js
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        financial: {
          positive: '#22c55e',
          negative: '#ef4444', 
          neutral: '#94a3b8',
        },
        surface: {
          DEFAULT: '#1e293b',
          hover: '#334155',
          active: '#4755692a',
        },
        accent: {
          DEFAULT: '#f59e0b',
          hover: '#d97706',
          muted: '#fbbf2440',
          text: '#fbbf24',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'skeleton': 'skeleton 1.5s ease-in-out infinite',
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },
      keyframes: {
        skeleton: {
          '0%, 100%': { opacity: '0.4' },
          '50%': { opacity: '0.8' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
    },
  },
  plugins: [],
}
```

### COMPONENTES DEL DESIGN SYSTEM

| Componente | Variantes | Estados | Props clave |
|---|---|---|---|
| **Button** | primary, secondary, ghost, danger | default, hover, active, disabled, loading | `size: sm/md/lg`, `icon`, `fullWidth` |
| **Card** | default, interactive, selected | default, hover, selected | `padding: sm/md/lg`, `as: div/button/a` |
| **Input** | outlined, filled | default, focus, error, disabled | `icon`, `label`, `helperText`, `error` |
| **Select** | native, custom | default, focus, error, disabled | `options`, `placeholder`, `searchable` |
| **Table** | default, compact | — | `columns`, `data`, `sortable`, `stickyHeader` |
| **Badge** | default, success, warning, danger, info | — | `size: sm/md`, `dot`, `removable` |
| **Skeleton** | text, card, table-row, chart | — | `variant`, `width`, `height`, `count` |
| **Modal** | default, fullscreen | open, closing | `title`, `description`, `size`, `closeOnOverlay` |
| **Tabs** | underline, pill | active, inactive, hover | `tabs[]`, `defaultIndex`, `onChange` |
| **Tooltip** | top, bottom, left, right | — | `content`, `delay` |
| **EmptyState** | default, search, error | — | `icon`, `title`, `description`, `action` |
| **ErrorBoundary** | — | — | `fallback`, `onError` |

### DATA TABLE (SCREENER) — DISEÑO

```
┌──────────────────────────────────────────────────────────────────┐
│ [A] Header                                                        │
│ Logo  [🔍 Buscar ticker...]         Screener  Dashboard  [👤] ☀️ │
├───────┬──────────────────────────────────────────────────────────┤
│ [B]   │ [C] Main Content                                         │
│ Side  │                                                          │
│ bar   │ Cobertura: 415 tickers              [Export CSV] [⚙️]    │
│       │ ┌────────┬─────────┬──────┬──────┬──────┬──────┬──────┐ │
│ mini  │ │ Ticker▲│ Nombre  │ PER  │ ROE  │ Marg │ D/E  │ ... │ │
│       │ ├────────┼─────────┼──────┼──────┼──────┼──────┼──────┤ │
│ Screener│ AAPL  │ Apple   │ 28.5 │ 0.45 │ 0.25 │ 1.2  │ ... │ │ ← hover: bg-surface-hover
│       │ │ GGAL   │ Grupo.. │ 12.3 │ 0.22 │ 0.18 │ 2.1  │     │ │
│ Dashbd │ │ MELI  │ Mercado │ 45.1 │ 0.38 │ 0.12 │ 0.8  │     │ │
│       │ └────────┴─────────┴──────┴──────┴──────┴──────┴──────┘ │
│ Pricing│ Mostrando 1-100 de 415       ← 1 2 3 4 5 ... →         │
│       │                                                          │
│ [👤]  │                                                          │
├───────┴──────────────────────────────────────────────────────────┤
│ [D] Footer minimal                                               │
│ Argfy © 2026 · Data from SEC EDGAR · Terms · Privacy            │
└──────────────────────────────────────────────────────────────────┘
```

---

## SECCIÓN 9 — NUEVA UX/UI PROPUESTA

### Navegación: Antes vs Después

| Antes | Después |
|---|---|
| Header: Logo, search, 7 nav links + auth + theme | Header: Logo, TickerSearch global, [Screener, Dashboard, Pricing], [Login/Account], theme |
| 3 marquees fijas (50px c/u) | 1 MarqueeBar configurable (toggleable, colapsable) |
| SecondaryNav: 10 tabs decorativos | ❌ Eliminado |
| Sin sidebar | Sidebar collapsible: Screener, Dashboard, Watchlists, API, Account |
| Footer enorme con newsletter, redes, disclaimer | Footer minimal: copyright + links legales |

### Layout: Antes vs Después

```
ANTES (layout.tsx):
┌──────────────────────────────────────────────┐
│ Header (saturado, 7 links)                   │
├──────────────────────────────────────────────┤
│ Marquee #1 (International, celeste, 50px)    │
├──────────────────────────────────────────────┤
│ Marquee #2 (ArgentineEconomic, white, 50px)  │
├──────────────────────────────────────────────┤
│ Marquee #3 (ArgentineStocks, celeste, 50px)  │
├──────────────────────────────────────────────┤
│ SecondaryNav (10 tabs, no funcional)         │
├──────────────────────────────────────────────┤
│ Main content (full width, sin sidebar)       │
├──────────────────────────────────────────────┤
│ Footer (enorme)                              │
└──────────────────────────────────────────────┘

DESPUÉS (layout.tsx):
┌──────────────────────────────────────────────────┐
│ Header minimal (logo + search + 3 links + auth)  │
├──────┬───────────────────────────────────────────┤
│      │ MarqueeBar (toggleable, 1 línea, 32px)    │
│ Side │───────────────────────────────────────────│
│ bar  │ Main content (max-w-7xl centered)         │
│ (col- │                                           │
│ laps) │ ┌──────┐ ┌──────┐ ┌──────┐               │
│       │ │ Card │ │ Card │ │ Card │               │
│       │ └──────┘ └──────┘ └──────┘               │
│       │                                           │
│       │ ┌─────────────────────────────────────┐  │
│       │ │ Data Table / Chart / Content        │  │
│       │ └─────────────────────────────────────┘  │
├───────┴───────────────────────────────────────────┤
│ Footer minimal                                    │
└──────────────────────────────────────────────────┘
```

### Homepage: Antes vs Después

| Antes (10 secciones) | Después (3 secciones + 1 colapsable) |
|---|---|
| Hero + 4 action cards | Hero minimal: "Análisis fundamental de CEDEARs" + 1 CTA → Screener |
| EconomicDataCards (6 cards) | Screener Preview: top 5 CEDEARs por PER (live, dinámico) |
| CEDEARs Leaderboard (tabla) | Quick Stats: 4 métricas clave (tickers, ratios promedio, etc.) |
| CedearsLeaderboard duplicado | Economic Dashboard (colapsado por defecto) |
| BanksSection (hardcoded) | ❌ Eliminado |
| GovernmentSection (hardcoded) | ❌ Eliminado |
| BCRASection (hardcoded) | ❌ Eliminado |
| EconomicsSection (hardcoded) | ❌ Eliminado |
| FinancesSection (hardcoded) | ❌ Eliminado |
| MarketsSection (hardcoded) | ❌ Eliminado |
| DailyEconomicData (hardcoded) | ❌ Eliminado |
| NewsSection (API + fallback) | Mantener, refactorizar |

### Interacción

| Feature | Implementación |
|---|---|
| Keyboard navigation | Tab + arrow keys en tablas, Enter para seleccionar, Escape para modales |
| Command palette (⌘K) | Zustand uiStore + Modal + fuzzy search de tickers/rutas/acciones |
| Persistent filters | Zustand persist middleware + URL sync |
| Smooth transitions | CSS transitions + framer-motion para modales/sidebar |
| Skeleton streaming | Suspense boundaries + Skeleton components |
| Responsive | Mobile: sidebar se convierte en drawer, tabla horizontal scroll |
| Empty states | EmptyState component con icono + mensaje + CTA |
| Error states | ErrorBoundary global + toast notifications |
| Loading states | Skeleton por tipo (card, table-row, chart) |

---

## SECCIÓN 10 — PLAN DE MIGRACIÓN INCREMENTAL

### FASES

```
Fase 0 (Día 0-1): Quick Wins Técnicos
    │
    ▼
Fase 1 (Día 1-3): Limpieza + Foundation
    │
    ▼
Fase 2 (Día 3-6): Design System v1
    │
    ▼
Fase 3 (Día 6-9): Layout + Navigation
    │
    ▼
Fase 4 (Día 9-11): API Layer Unification
    │
    ▼
Fase 5 (Día 11-13): Screener + Research Refactor
    │
    ▼
Fase 6 (Día 13-15): Backend Cleanup
    │
    ▼
Fase 7 (Día 15-20): Premium Polish
```

### FASE 0 — QUICK WINS TÉCNICOS (Día 0-1)

| # | Tarea | Archivo | Esfuerzo | Riesgo | Rollback | Feature Flag |
|---|---|---|---|---|---|---|
| Q1 | Fix `require_feature` bug | `backend/app/middleware/feature_gate.py` | 15min | 🟡 Medio — revisar dependencias | Git revert | No |
| Q2 | Implement rate limiter real (slowapi) | `backend/app/middleware/rate_limit_middleware.py` | 30min | 🟡 Bajo — no rompe | Git revert | `RATE_LIMIT_ENABLED` |
| Q3 | Fix seed_plans (upsert en startup) | `backend/app/scripts/seed_plans.py` | 15min | 🟢 Ninguno | Git revert | No |
| Q4 | Fix import roto economic_cards | `backend/app/routers/economic_cards.py` | 15min | 🟢 Bajo — nadie lo usa | Comentar línea | No |
| Q5 | Eliminar categories.py (TS en Python) | `backend/app/config/categories.py` | 5min | 🟢 Ninguno | Git revert | No |
| Q6 | Fix import roto useBCRAReal.ts | `frontend/src/hooks/useBCRAReal.ts` | 5min | 🟢 Bajo | Git revert | No |
| Q7 | Configurar Sentry correctamente | `backend/app/main.py` | 30min | 🟢 Bajo | Comentar | `SENTRY_DSN` |

**Total Fase 0: ~2h — Sprint 1**

### FASE 1 — LIMPIEZA + FOUNDATION (Día 1-3)

| # | Tarea | Esfuerzo | Riesgo | Feature Flag |
|---|---|---|---|---|
| 1.1 | Eliminar 4 marquees legacy (Argentina, Global, TradingView, CustomArgentina) | 10min | 🟢 Ninguno | No |
| 1.2 | Eliminar MarqueeControlPanel | 5min | 🟢 Ninguno | No |
| 1.3 | Consolidar 3 marquees → 1 MarqueeBar configurable | 2h | 🟡 Medio — perder algún dato | `MARQUEE_ENABLED` |
| 1.4 | Eliminar SecondaryNav | 10min | 🟢 Ninguno | No |
| 1.5 | Eliminar secciones homepage estáticas (Banks, Government, etc.) | 1h | 🟡 Medio — homepage cambia visualmente | `HOMEPAGE_V2` |
| 1.6 | Eliminar dependencia @headlessui/react | 5min | 🟢 Ninguno | No |
| 1.7 | Split components/index.tsx → types/, config/, hooks/ separados | 3h | 🟡 Medio — imports rotos temporalmente | No (atomic commit) |
| 1.8 | Configurar ESLint unificado (solo flat config) | 30min | 🟢 Bajo | No |
| 1.9 | Agregar next.config.js typecheck/lint en build (quitar ignore) | 15min | 🟡 Medio — warnings van a romper build | Gradual |

**Total Fase 1: ~8h — Sprint 1-2**

### FASE 2 — DESIGN SYSTEM v1 (Día 3-6)

| # | Tarea | Esfuerzo | Riesgo | Feature Flag |
|---|---|---|---|---|
| 2.1 | Implementar `styles/tokens.css` con todos los tokens | 1h | 🟢 Bajo | No |
| 2.2 | Extender Tailwind config con colores semánticos + financial colors | 30min | 🟢 Bajo | No |
| 2.3 | Build Button component (3 variantes, 3 sizes, loading, icon) | 1.5h | 🟢 Bajo | No |
| 2.4 | Build Card component (3 padding variants, interactive) | 45min | 🟢 Bajo | No |
| 2.5 | Build Input component (with label, error, icon, sizes) | 1h | 🟢 Bajo | No |
| 2.6 | Build Badge component (5 variants, with dot, removable) | 45min | 🟢 Bajo | No |
| 2.7 | Build Skeleton component (4 variants: text, card, table-row, chart) | 1h | 🟢 Bajo | No |
| 2.8 | Build Modal component (size variants, closeOnOverlay, portal) | 1.5h | 🟡 Bajo | No |
| 2.9 | Build Tabs component (underline + pill variants) | 1h | 🟢 Bajo | No |
| 2.10 | Build EmptyState component (default, search, error variants) | 45min | 🟢 Bajo | No |
| 2.11 | Build ErrorBoundary component | 30min | 🟢 Bajo | No |
| 2.12 | Build Tooltip component | 45min | 🟢 Bajo | No |
| 2.13 | Build LoadingSpinner (refactor) | 15min | 🟢 Bajo | No |

**Total Fase 2: ~12h — Sprint 2-3**

### FASE 3 — LAYOUT + NAVIGATION (Día 6-9)

| # | Tarea | Esfuerzo | Riesgo | Feature Flag |
|---|---|---|---|---|
| 3.1 | Redesign Header (minimal: logo + TickerSearch + 3 nav links + auth) | 2h | 🟡 Medio — cambiar markup puede afectar CSS | `LAYOUT_V2` |
| 3.2 | Build Sidebar component (collapsible, icon+label, active state) | 3h | 🟡 Medio — nuevo elemento de layout | `SIDEBAR_ENABLED` |
| 3.3 | Implement Zustand stores (authStore + uiStore + filterStore) | 2h | 🟡 Medio — reemplazar AuthContext | `ZUSTAND_AUTH` |
| 3.4 | Refactor Providers.tsx (Queries + Zustand + Theme) | 1h | 🟡 Medio — providers cambian | No |
| 3.5 | Refactor layout.tsx (new header + sidebar + 1 marquee + footer) | 2h | 🟡 Medio — layout root cambia | `LAYOUT_V2` |
| 3.6 | Implement MarqueeBar (1 componente, data configurable) | 1h | 🟡 Bajo | `MARQUEE_ENABLED` |
| 3.7 | Refactor homepage (3 secciones + economic dashboard collapsible) | 3h | 🟡 Medio — homepage cambia radicalmente | `HOMEPAGE_V2` |
| 3.8 | Agregar Skeleton loading a homepage (streaming) | 1h | 🟢 Bajo | No |
| 3.9 | Agregar ErrorBoundary global a app/layout.tsx | 30min | 🟢 Bajo | No |

**Total Fase 3: ~16h — Sprint 3-4**

### FASE 4 — API LAYER UNIFICATION (Día 9-11)

| # | Tarea | Esfuerzo | Riesgo | Feature Flag |
|---|---|---|---|---|
| 4.1 | Consolidar API clients (eliminar axios `apiClient`, unificar en fetch+Zod) | 3h | 🟡 Medio — revisar todos los consumers | No (atomic) |
| 4.2 | Mover API functions a `lib/api/client.ts` + domain files | 1h | 🟢 Bajo | No |
| 4.3 | Refactor hooks legacy a TanStack Query (useIndicators, useBCRAReal, etc.) | 2h | 🟡 Medio — cambiar lógica de fetching | No |
| 4.4 | Agregar auth interceptor al API client (JWT + API key) | 30min | 🟡 Medio — auth puede romperse | No |
| 4.5 | Refactor EconomicDataCards (API real, eliminar fallback hardcoded) | 1.5h | 🟢 Bajo | No |
| 4.6 | Refactor NewsSection (API real, eliminar fallback hardcoded) | 1h | 🟢 Bajo | No |

**Total Fase 4: ~9h — Sprint 4-5**

### FASE 5 — SCREENER + RESEARCH REFACTOR (Día 11-13)

| # | Tarea | Esfuerzo | Riesgo | Feature Flag |
|---|---|---|---|---|
| 5.1 | Refactor ScreenerTable con nuevo Table component + column sorting visual | 2h | 🟡 Medio — tabla core, test exhaustivo | `SCREENER_V2` |
| 5.2 | Keyboard navigation en screener (↑↓ para rows, Enter para detail) | 1.5h | 🟢 Bajo | No |
| 5.3 | Saved filters (Zustand persist + load/delete) | 2h | 🟢 Bajo | `SAVED_FILTERS` |
| 5.4 | Refactor FilterSidebar (mejorar mobile drawer) | 1h | 🟢 Bajo | No |
| 5.5 | Agregar skeleton loading a screener | 30min | 🟢 Bajo | No |
| 5.6 | Refactor ticker detail page (TickerHeader, KeyMetrics, PriceChart layout) | 3h | 🟡 Medio — detalle core | `DETAIL_V2` |
| 5.7 | Mejorar empty states del screener (sin resultados, error, loading) | 30min | 🟢 Bajo | No |

**Total Fase 5: ~10h — Sprint 5-6**

### FASE 6 — BACKEND CLEANUP (Día 13-15)

| # | Tarea | Esfuerzo | Riesgo | Rollback |
|---|---|---|---|---|
| 6.1 | Deprecar routers legacy (expanded_indicators, unified_economic, data, economic_cards) | 1h | 🟡 Medio — check consumers primero | Git revert |
| 6.2 | Unificar schedulers (eliminar UnifiedScheduler, migrar tasks a APScheduler) | 2h | 🟡 Medio — tasks pueden perderse | Git revert |
| 6.3 | Eliminar endpoints duplicados en admin router | 30min | 🟢 Bajo | Git revert |
| 6.4 | Eliminar servicios no usados (dollar_multi_source, http_factory, bcra_massive, etc.) | 30min | 🟢 Bajo | Git revert |
| 6.5 | Agregar tests de ratio engine (PER, ROE5y, CAGR, Deuda/EBITDA) | 3h | 🟢 Bajo | No |
| 6.6 | Configurar Sentry correctamente en backend | 30min | 🟢 Bajo | Comentar |

**Total Fase 6: ~7h — Sprint 6**

### FASE 7 — PREMIUM POLISH (Día 15-20)

| # | Tarea | Esfuerzo | Riesgo |
|---|---|---|---|
| 7.1 | Command palette (⌘K) — Zustand + Modal + fuzzy search | 3h | 🟢 Bajo |
| 7.2 | Keyboard navigation global (tabs, modales, tables) | 3h | 🟢 Bajo |
| 7.3 | Smooth transitions (framer-motion para sidebar, modales, tabs) | 2h | 🟢 Bajo |
| 7.4 | Light mode polish (verificar todos los componentes en light) | 2h | 🟢 Bajo |
| 7.5 | Responsive audit (mobile: sidebar→drawer, tables→horizontal scroll) | 2h | 🟢 Bajo |
| 7.6 | Empty states en todas las páginas | 1h | 🟢 Bajo |
| 7.7 | Error boundaries en todas las páginas | 1h | 🟢 Bajo |
| 7.8 | Performance audit (Lighthouse, bundle analysis, Web Vitals) | 2h | 🟢 Bajo |
| 7.9 | Code splitting y lazy loading de páginas no core | 1h | 🟢 Bajo |
| 7.10 | Documentación de decisiones + changelog | 1h | 🟢 Bajo |

**Total Fase 7: ~18h — Sprint 7-8**

---

## SECCIÓN 11 — REFACTOR ROADMAP POR FASES (30/60/90)

```
DÍA 0 ────────────────────────────────────────────────────────────── DÍA 90

┌───────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┐
│  F0   │  F1   │  F2   │  F3   │  F4   │  F5   │  F6   │  F7   │       │
│ Quick │ Clean │  DS   │Layout │ API   │Screener│Backend│Premium│ Done  │
│ Wins  │up     │  v1   │+ Nav  │ Layer │Refactor│ Clean │Polish │       │
├───────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┤       │
│ 2h    │ 8h    │ 12h   │ 16h   │ 9h    │ 10h   │ 7h    │ 18h   │       │
└───────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┘       │
                                                                        │
◄─── 30 DÍAS (F0+F1+F2+F3) ───►◄─── 60 DÍAS (F4+F5+F6) ───►◄── 90 DÍAS (F7) ►
```

### DÍA 0-30: FOUNDATION + QUICK WINS

| Semana | Fase | Entregas concretas |
|---|---|---|
| Semana 1 | F0 + F1 | Rate limiter funcionando, feature gates destrabados, 8 componentes legacy eliminados, homepage simplificada (de 10 secciones a 3), components/index.tsx spliteado |
| Semana 2 | F2 (inicio) | tokens.css, Tailwind extend, 10 componentes DS (Button, Card, Input, Badge, Skeleton, Modal, Tabs, EmptyState, ErrorBoundary, Tooltip) |
| Semana 3 | F2 (fin) + F3 (inicio) | Header minimal rediseñado, Sidebar collapsible, Zustand stores (auth+ui+filters), layout.tsx renovado |
| Semana 4 | F3 (fin) | MarqueeBar única, homepage v2 (3 secciones), skeletons, error boundaries |

**KPIs Semana 4:**
- ✅ 0 incidentes críticos por rollout
- ✅ Layout visualmente consistente en todas las páginas
- ✅ LCP < 3.0s (vs baseline ~4s)
- ✅ Reducción de ~40% de clutter visual en homepage

### DÍA 31-60: CORE PRODUCT REFACTOR

| Semana | Fase | Entregas concretas |
|---|---|---|
| Semana 5 | F4 | API layer unificada (sin axios), hooks legacy migrados a TanStack Query, EconomicDataCards y NewsSection refactorizados |
| Semana 6 | F5 (inicio) | ScreenerTable v2 con Table DS, keyboard nav en screener, filterStore persistente |
| Semana 7 | F5 (fin) | Ticker detail refactorizado (layout nuevo, KeyMetrics, PriceChart), saved filters funcionales |
| Semana 8 | F6 | Backend cleanup: routers legacy deprecados, schedulers unificados, admin deduplicado, tests de ratio engine agregados |

**KPIs Semana 8:**
- ✅ -30% tiempo de tarea en screener (medido vs baseline)
- ✅ INP < 200ms en páginas core
- ✅ 0 P1 incidents por releases de refactor
- ✅ Backend legacy reducido en ~30% (líneas eliminadas)

### DÍA 61-90: HARDENING + PREMIUM

| Semana | Fase | Entregas concretas |
|---|---|---|
| Semana 9 | F7 (inicio) | Command palette (⌘K), keyboard navigation global, framer-motion transitions |
| Semana 10 | F7 (mitad) | Light mode audit + fix, responsive audit, empty/error states en todas las páginas |
| Semana 11 | F7 (fin) | Performance audit (Lighthouse ≥ 85), code splitting, bundle optimization |
| Semana 12 | Consolidación | Documentación final, convenciones definitivas, backlog post-90 días, decommission de legacy remanente |

**KPIs Semana 12:**
- ✅ LCP < 2.5s (p75)
- ✅ INP < 200ms (p75)
- ✅ CLS < 0.1 (p75)
- ✅ Bundle JS inicial -30% vs baseline
- ✅ Cobertura de flujos core con smoke tests ≥ 80%
- ✅ Errores frontend por 1k sesiones -40%
- ✅ Deuda legacy crítica reducida 50%

---

## SECCIÓN 12 — RIESGOS Y MITIGACIONES

### POR MÓDULO

| Módulo | Riesgo | Prob | Impacto | Mitigación | Rollback |
|---|---|---|---|---|---|
| **feature_gate.py** | Fix rompe dependencias ocultas de `Depends()` | 🟡 Media | 🔴 Alto | Revisar todos los callers antes del fix | Git revert + deploy |
| **rate_limit_middleware.py** | Implementación incorrecta bloquea requests legítimos | 🟡 Media | 🔴 Alto | Feature flag `RATE_LIMIT_ENABLED`, empezar con límites altos, monitorear | Disable flag |
| **Layout refactor (F3)** | Sidebar + nuevo header rompen CSS de páginas existentes | 🟡 Media | 🟡 Medio | Feature flag `LAYOUT_V2`, test en staging primero | Disable flag |
| **Zustand stores** | Reemplazar AuthContext rompe auth flow | 🟡 Media | 🔴 Alto | Feature flag `ZUSTAND_AUTH`, convivir ambos sistemas 1 semana | Disable flag |
| **Screener refactor (F5)** | ScreenerTable v2 tiene bug de paginación/sorting | 🟡 Baja | 🔴 Alto | Test exhaustivo en staging, comparar resultados vs v1 | Flag `SCREENER_V2` |
| **Backend cleanup (F6)** | Eliminar router que algún consumer usa | 🟡 Baja | 🟡 Medio | Deprecar con warning 1 semana antes, check logs de uso | Git revert |
| **UnifiedScheduler removal** | Task de BCRA update no migrada a APScheduler | 🟡 Media | 🟡 Medio | Verificar que APScheduler tenga todas las tasks | Restaurar archivo |
| **API layer unification** | Romper consumers del API client legacy | 🟡 Media | 🟡 Medio | Refactor por archivo, no todo junto, test cada cambio | Git revert parcial |
| **Deploy** | Coolify webhook deploy falla | 🟡 Baja | 🔴 Alto | Deploy manual si es necesario, rollback con compose anterior | Redeploy versión anterior |

### PLAN DE ROLLBACK GENERAL

```
1. Feature flags en cada cambio significativo
   - Si algo falla → DISABLE FLAG → sistema vuelve al comportamiento anterior
   - Sin downtime, sin redeploy (si el flag es runtime)

2. Para cambios sin flag (atomicos):
   - Git revert del commit específico
   - Redeploy vía Coolify webhook
   - Tiempo estimado: < 15 min

3. Para cambios de backend sin flag:
   - Mantener versión anterior del container
   - Coolify permite rollback a versión previa en 1 click
   - Tiempo estimado: < 5 min

4. Escenario peor caso:
   - Bug crítico en producción que bloquea screener
   - Rollback: git checkout al tag anterior, redeploy
   - Tiempo: < 20 min
```

### MATRIZ DE DECISIÓN — ¿SALE A PRODUCCIÓN?

```
¿Tiene feature flag?  ──Sí──→ ¿Probado en staging? ──Sí──→ ✅ Sale
     │                          │
     No                         No
     │                          │
     ▼                          ▼
  ¿Es reversible             No sale → Fix → Re-test
  en < 15 min?
     │
  Sí──→ ✅ Sale con monitoreo intensivo (30 min post-deploy)
     │
     No──→ ❌ No sale → Test en staging → Re-evaluar
```

---

## SECCIÓN 13 — ÁRBOL IDEAL DEL REPOSITORIO

```
argfy/
├── README.md
├── .github/
│   └── workflows/
│       ├── deploy.yml          # Sin cambios
│       └── test.yml            # Sin cambios
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # Simplificado, routers limpios
│   │   ├── database.py         # Sin cambios
│   │   ├── models.py           # Sin cambios
│   │   ├── scheduler.py        # Solo APScheduler
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── config.py       # Sin cambios
│   │   │   └── indicators_mapping.py
│   │   ├── middleware/
│   │   │   ├── auth.py         # Sin cambios
│   │   │   ├── feature_gate.py # FIXED
│   │   │   ├── rate_limit_middleware.py  # IMPLEMENTED
│   │   │   └── logging_middleware.py
│   │   ├── routers/
│   │   │   ├── fundamentals.py # CORE
│   │   │   ├── auth.py
│   │   │   ├── billing.py
│   │   │   ├── admin.py        # Limpiado
│   │   │   ├── health.py
│   │   │   ├── indicators.py
│   │   │   ├── system.py
│   │   │   └── bcra_real.py
│   │   ├── services/
│   │   │   ├── auth.py
│   │   │   ├── billing.py
│   │   │   ├── bcra_service.py
│   │   │   ├── bcra_expanded_service.py
│   │   │   ├── dolar_blue_service.py
│   │   │   ├── cache_service.py
│   │   │   └── integrated_data_service.py
│   │   ├── jobs/
│   │   │   ├── refresh_prices.py
│   │   │   ├── refresh_sec_filings.py
│   │   │   ├── recalc_ratios.py
│   │   │   └── quality_check.py
│   │   └── utils/
│   │       └── emoji_log.py
│   ├── scripts/
│   │   ├── seed_plans.py       # FIXED
│   │   └── seed_fundamentals.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_fundamentals.py
│   │   ├── test_main.py
│   │   ├── test_ratios.py
│   │   └── test_ratios_engine.py  # NUEVO
│   ├── db/
│   │   └── schema.sql          # Expandido con auth/billing tables
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx      # Refactorizado
│   │   │   ├── page.tsx        # Homepage v2
│   │   │   ├── globals.css
│   │   │   ├── cedears/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [byma_ticker]/
│   │   │   │       └── page.tsx  # Refactorizado
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── auth/
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── register/page.tsx
│   │   │   ├── pricing/
│   │   │   │   └── page.tsx
│   │   │   └── account/
│   │   │       ├── page.tsx
│   │   │       ├── billing/page.tsx
│   │   │       └── api-keys/page.tsx
│   │   ├── components/
│   │   │   ├── ui/              # Design System
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Badge.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Select.tsx
│   │   │   │   ├── Table.tsx
│   │   │   │   ├── Skeleton.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── Tabs.tsx
│   │   │   │   ├── Tooltip.tsx
│   │   │   │   ├── Command.tsx
│   │   │   │   ├── EmptyState.tsx
│   │   │   │   ├── ErrorBoundary.tsx
│   │   │   │   └── LoadingSpinner.tsx
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx     # Refactorizado
│   │   │   │   ├── Sidebar.tsx    # NUEVO
│   │   │   │   ├── Footer.tsx     # Simplificado
│   │   │   │   ├── Providers.tsx  # Refactorizado
│   │   │   │   └── MarqueeBar.tsx # Unificado
│   │   │   ├── screener/
│   │   │   │   ├── FilterSidebar.tsx
│   │   │   │   ├── ScreenerTable.tsx  # Refactorizado
│   │   │   │   ├── RatioCell.tsx
│   │   │   │   ├── CoverageStats.tsx  # NUEVO
│   │   │   │   └── SavedFilters.tsx   # NUEVO
│   │   │   ├── research/
│   │   │   │   ├── TickerHeader.tsx   # NUEVO
│   │   │   │   ├── KeyMetrics.tsx     # NUEVO
│   │   │   │   ├── PriceChart.tsx
│   │   │   │   ├── MetricHistoryChart.tsx
│   │   │   │   ├── FinancialTable.tsx # NUEVO
│   │   │   │   └── CompanyProfile.tsx # NUEVO
│   │   │   ├── dashboard/
│   │   │   │   ├── DashboardGrid.tsx
│   │   │   │   └── MetricCard.tsx
│   │   │   └── shared/
│   │   │       ├── TickerSearch.tsx
│   │   │       └── AuthGuard.tsx
│   │   ├── hooks/
│   │   │   ├── useScreener.ts
│   │   │   ├── useTickerDetail.ts
│   │   │   ├── useCoverage.ts
│   │   │   ├── usePriceHistory.ts
│   │   │   ├── useMetricHistory.ts
│   │   │   ├── useAuth.ts         # Refactorizado (Zustand)
│   │   │   ├── useDebounce.ts
│   │   │   └── useKeyboard.ts     # NUEVO
│   │   ├── stores/
│   │   │   ├── authStore.ts       # NUEVO
│   │   │   ├── uiStore.ts         # NUEVO
│   │   │   └── filterStore.ts     # NUEVO
│   │   ├── lib/
│   │   │   ├── api/
│   │   │   │   ├── client.ts      # Unificado
│   │   │   │   ├── fundamentals.ts
│   │   │   │   ├── auth.ts
│   │   │   │   ├── billing.ts
│   │   │   │   └── admin.ts
│   │   │   ├── types/
│   │   │   │   ├── screener.ts
│   │   │   │   ├── auth.ts
│   │   │   │   └── common.ts
│   │   │   ├── utils/
│   │   │   │   ├── cn.ts
│   │   │   │   ├── formatters.ts
│   │   │   │   └── constants.ts
│   │   │   └── validations/
│   │   │       └── schemas.ts
│   │   ├── config/
│   │   │   ├── navigation.ts
│   │   │   └── theme.ts
│   │   └── styles/
│   │       ├── globals.css
│   │       └── tokens.css        # NUEVO
│   ├── public/
│   ├── Dockerfile
│   ├── next.config.js            # Fixed (typecheck/lint en build)
│   ├── tailwind.config.js        # Extended
│   ├── tsconfig.json
│   └── package.json              # Sin @headlessui, sin axios
│
├── deployment/
│   ├── docker-compose.coolify.yml
│   ├── docker-compose.yml
│   ├── docker-compose.override.yml
│   ├── coolify/
│   │   ├── README.colaborador.md
│   │   ├── docker-compose.coolify.template.yml
│   │   ├── *.env.example
│   │   ├── argfy.secrets.template.md
│   │   └── colaboradores/
│   ├── hetzner/
│   │   ├── provision.sh
│   │   └── README.md
│   └── backup.sh
│
└── plan/
    ├── plan_saneamiento.md
    ├── plan_devops_vps_opencode.md
    ├── plan_frontend_16_05_2026_opencode.md
    ├── plan_reingenieria_incremental.md   # NUEVO (este documento)
    └── ...
```

---

## SECCIÓN 14 — CONVENCIONES DE CÓDIGO

### FRONTEND

| Convención | Regla |
|---|---|
| **Naming archivos** | `kebab-case.tsx` para componentes, `camelCase.ts` para hooks/utils |
| **Naming componentes** | `PascalCase` — `ScreenerTable`, `FilterSidebar` |
| **Naming funciones/vars** | `camelCase` — `formatValue`, `syncFilters` |
| **Naming tipos** | `PascalCase` con sufijo de propósito — `ScreenerFilters`, `TickerResponse` |
| **Un componente por archivo** | Excepción: utilities pequeñas del mismo dominio |
| **Default exports** | Para componentes páginables (Next.js App Router) |
| **Named exports** | Para utilities, hooks, tipos |
| **Orden de imports** | React → Next → librerías externas → @/components/ui → @/components → @/hooks → @/stores → @/lib → @/config → @/styles |
| **Server Component por defecto** | Solo agregar `"use client"` si usa: hooks, eventos, estado, efectos |
| **TanStack Query** | StaleTime configurado por query (2min screener, 5min detalle, 10min coverage) |
| **Zustand stores** | Un store por dominio. Persist con `persist` middleware solo si necesario |
| **Design System** | Todo componente usa tokens CSS. No magic numbers |
| **CSS** | Tailwind utility-first. `cn()` para merging condicional. No CSS modules |
| **Responsive** | Mobile-first. Sidebar→drawer en < lg. Tables→horizontal scroll en < md |

### BACKEND

| Convención | Regla |
|---|---|
| **Python 3.11+** | Type hints obligatorios en todas las funciones |
| **FastAPI routers** | Prefijo + tags. Un archivo por dominio |
| **SQLAlchemy** | Async session. `get_db()` como dependency |
| **Services** | Clases con `__aenter__`/`__aexit__` para recursos |
| **Pydantic v2** | Schemas de request/response con validación |
| **Tests** | pytest + asyncio. Fixtures en conftest.py |
| **Logging** | `logger = logging.getLogger(__name__)` por módulo |
| **Errores** | HTTPException con detail descriptivo. Códigos REST estándar |

### GIT

| Convención | Regla |
|---|---|
| **Commits** | `tipo(scope): mensaje` — ej: `feat(screener): add column resize` |
| **Tipos** | `feat`, `fix`, `refactor`, `style`, `chore`, `docs`, `test` |
| **Branches** | `feature/xxx`, `fix/xxx`, `refactor/xxx`, `chore/xxx` |
| **PRs** | < 300 líneas. Reviewer mandatory |
| **Rollback commits** | Firmados con tag `vX.Y.Z-rollback` |

---

## SECCIÓN 15 — QUICK WINS DE ALTO IMPACTO

### TOP 10 (ordenados por impacto/esfuerzo)

| # | Quick Win | Esfuerzo | Impacto | Área | Flag |
|---|---|---|---|---|---|
| **1** | Fix `require_feature` bug | 15min | 🔴 Destraba monetización | Backend | No |
| **2** | Implement rate limiter real | 30min | 🔴 Destraba planes free/pro | Backend | `RATE_LIMIT_ENABLED` |
| **3** | Seed PlanFeature defaults | 15min | 🔴 Destraba feature gates | Backend | No |
| **4** | Eliminar 3 marquees → 1 | 2h | 🟡 Reduce ruido visual 50% | Frontend | No |
| **5** | Eliminar SecondaryNav | 10min | 🟡 Menos clutter en layout | Frontend | No |
| **6** | Eliminar homepage sections estáticas | 1h | 🟡 Homepage más limpia, -60% contenido muerto | Frontend | `HOMEPAGE_V2` |
| **7** | Split `components/index.tsx` | 3h | 🟢 +Maintainability, -450 líneas monolíticas | Frontend | No |
| **8** | Agregar Skeleton loading a homepage | 1h | 🟢 UX premium inmediato | Frontend | No |
| **9** | Agregar ErrorBoundary a todas las páginas | 1h | 🟢 UX premium, evita white screens | Frontend | No |
| **10** | Fix import useBCRAReal.ts | 5min | 🟢 Destraba BCRA dashboard | Frontend | No |

### OTROS QUICK WINS (BAJO ESFUERZO)

| Quick Win | Esfuerzo | Impacto |
|---|---|---|
| Eliminar @headlessui/react | 5min | 🟢 Menos deuda |
| Eliminar axios (transitivo) | 30min | 🟢 Menos deuda |
| Unificar ESLint config | 30min | 🟢 DevX |
| Agregar `next/dynamic` lazy loading a componentes pesados | 1h | 🟢 Performance |
| Configurar Sentry frontend | 30min | 🟢 Monitoreo |
| Agregar metadata a todas las páginas | 1h | 🟢 SEO |
| Cache headers en API responses | 30min | 🟢 Performance |

---

## SECCIÓN 16 — ESTIMACIÓN REALISTA

### POR FASE

| Fase | Descripción | Horas | Días | Dependencias | Paralelizable |
|---|---|---|---|---|---|
| F0 | Quick Wins técnicos | 2h | 0.5 | Ninguna | ✅ Con todas |
| F1 | Limpieza + Foundation | 8h | 2 | Ninguna | ✅ Con F2 |
| F2 | Design System v1 | 12h | 3 | Ninguna | ✅ Con F1 |
| F3 | Layout + Navigation | 16h | 4 | F2 (DS para componentes) | ❌ |
| F4 | API Layer Unification | 9h | 2.5 | Ninguna | ✅ Con F3 |
| F5 | Screener + Research Refactor | 10h | 2.5 | F2 (DS Table) + F4 (API) | ❌ |
| F6 | Backend Cleanup | 7h | 2 | Ninguna | ✅ Con F3 |
| F7 | Premium Polish | 18h | 4.5 | F2 (DS base) | ❌ |
| **Total** | | **82h** | **20 días** | | |

### POR RECURSO

| Escenario | Tiempo estimado | Costo relativo |
|---|---|---|
| 1 dev full-time | 20 días hábiles (4 semanas) | 1x |
| 2 devs en paralelo | 12 días hábiles (2.5 semanas) | 1.5x |
| 1 dev part-time (50%) | 8 semanas | 0.5x |
| 1 dev + 1 designer (paralelo) | 14 días hábiles (3 semanas) | 1.3x (mejor relación calidad/tiempo) |

### RANGO DE CONFIANZA

| Estimación | Días | Probabilidad |
|---|---|---|
| Optimista (sin blockers, sin bugs) | 14 días | 20% |
| **Realista (con bugs, PR reviews, fixes)** | **20 días** | **60%** |
| Pesimista (issues imprevistos, cambios de scope) | 28 días | 20% |

---

## SECCIÓN 17 — ESTRATEGIA POST-DEADLINE

### INMEDIATO (post Consigna 4.0 — Semanas 1-4)

1. **Semanas 1-2**: Fase 0 + Fase 1 implementadas en producción
   - Rate limiter, feature gates, seed plans destrabando monetización
   - Homepage limpia, marquees consolidadas, SecondaryNav eliminado
2. **Semanas 3-4**: Fase 2 + inicio Fase 3
   - Design System v1 en uso en nuevas páginas
   - Nuevo layout (header + sidebar) en producción con flag

### CORTO PLAZO (Mes 2-3)

3. Fase 4 + Fase 5: API layer unificada, screener v2
4. Fase 6: Backend cleanup completado
5. Watchlists feature (tabla user-specific, Zustand persist + API)
6. Portfolio tracking básico (holdings + returns)

### MEDIANO PLAZO (Mes 4-6)

7. Fase 7: Premium polish (⌘K, keyboard nav, transitions)
8. Pasar tests a coverage > 80%
9. Migrar APScheduler a Celery (Redis ya en infra)
10. Staging environment (segundo VPS o preview deployments en Coolify)
11. Internacionalización (en) para expansión internacional

### LARGO PLAZO (Q3-Q4 2026)

12. Coolify fork (WebsHooks Platform) — postergado hasta estabilizar Argfy
13. Alerts system (precio objetivo, ratio threshold, email/web push)
14. Comparador de tickers (side-by-side)
15. API pública documentada (OpenAPI + developer portal)
16. Mobile web app (PWA primero, React Native después)

### LO QUE NUNCA HAY QUE HACER

| ❌ No hacer | Por qué |
|---|---|
| Rewrite total del frontend | Riesgo enorme, zero business value durante meses |
| Migrar de Tailwind a otro CSS | Pérdida de tiempo, Tailwind es industry standard |
| Reemplazar Next.js | App Router es moderno y funciona |
| Reemplazar FastAPI | Backend sólido, buena performance |
| Migrar de PostgreSQL | Datos ya migrados, schema productivo |
| Agregar Kubernetes | 1 VPS, 3 containers, overkill total |
| Reemplazar Coolify antes del fork | Coolify funciona, fork es evolución no reemplazo |
| Reescribir charts desde cero | Recharts es suficiente, mejor wrapper components |
| Hacer "polish infinito" sin base arquitectónica | Primero estructura, después belleza |

---

## ENTREGABLES A-H (mapeados dentro de las 17 secciones)

| Entregable | Dónde está |
|---|---|
| **A. Auditoría completa** | Secciones 1+2 (diagnóstico + problemas) + Sección 15 (quick wins) |
| **B. Nueva arquitectura** | Sección 6 (frontend tree) + Sección 7 (backend tree) + state architecture diagram |
| **C. Plan de migración** | Secciones 10+11 (fases, roadmap, dependencias, rollback) |
| **D. Plan UI/UX** | Sección 9 (navegación antes/después, layout strategy, interacción) |
| **E. Mapa de eliminación** | Sección 4 (qué eliminar) + Sección 3 (qué mantener) |
| **F. Design System** | Sección 8 (tokens CSS, Tailwind extend, 13 componentes con variantes/estados) |
| **G. Refactor plan técnico** | Secciones 10+11 (pasos exactos, orden, riesgo por módulo) |
| **H. Árbol final del repo** | Sección 13 (árbol completo con todos los archivos) |

---

## KPI DASHBOARD (con metas y umbrales)

| KPI | Métrica | Baseline (estimado) | Meta 30d | Meta 60d | Meta 90d |
|---|---|---|---|---|---|
| **LCP** | p75 | ~4s | < 3.0s | < 2.5s | < 2.5s |
| **INP** | p75 | ~300ms | < 250ms | < 200ms | < 200ms |
| **CLS** | p75 | ~0.3 | < 0.15 | < 0.1 | < 0.1 |
| **JS Bundle** | KB inicial | ~250KB | < 200KB | < 180KB | < 160KB |
| **Screener task time** | segundos medios | ~45s | < 35s | < 30s | < 25s |
| **Errores frontend** | por 1k sesiones | ~20 | < 15 | < 12 | < 10 |
| **Incidentes P1** | por release | — | 0 | 0 | 0 |
| **Deuda legacy** | % líneas legacy | 100% | -30% | -50% | -60% |
| **Cobertura tests** | % flujos core | ~40% | 50% | 70% | 85% |

---

## GOVERNANCE Y CADENCIA OPERATIVA

| Ceremonia | Frecuencia | Duración | Participantes | Agenda |
|---|---|---|---|---|
| **Weekly Steering** | Semanal | 60min | Dev lead + PM + Founder | Estado por fase, riesgos nuevos, decisiones bloqueantes |
| **Demo Quincenal** | Cada 2 semanas | 30min | Equipo + Stakeholders | Vertical slices reales en staging/prod-flagged |
| **Release** | Semanal o bisemanal | — | Dev lead | Siempre con flags, release notes |
| **Post-mortem** | Por incidente P1 | 30min | Equipo | What happened, why, how to prevent |

### SEMÁFORO DE RIESGO POR MÓDULO

| Color | Significado | Acción |
|---|---|---|
| 🟢 Verde | Sin riesgo conocido | Deploy normal |
| 🟡 Amarillo | Riesgo monitoreado, mitigación lista | Deploy con monitoreo intensivo (30 min post) |
| 🔴 Rojo | Riesgo alto, mitigación no probada | No deploy. Reunión extraordinaria. |

### REGLA DE ORO

> Si un cambio no es reversible en menos de 15 minutos, no sale a producción.

---

## DEFINITION OF DONE (DoD) — por módulo/fase

Un módulo está "Done" solo si cumple **TODAS** estas condiciones:

### ✅ Funcional
- [ ] Flujo principal completo operando en entorno tipo producción
- [ ] Sin degradación de: auth, billing, APIs críticas, screener core
- [ ] Feature flag verificado (on = nuevo, off = comportamiento anterior)

### ✅ Técnico
- [ ] Código en estructura objetivo (o adaptador documentado con ticket de migración)
- [ ] Sin duplicación obvia de estado o lógica
- [ ] Tipado estricto en nuevas superficies (TypeScript strict mode)
- [ ] ESLint pasa sin warnings nuevos

### ✅ UX/UI
- [ ] Componente/página usa tokens del Design System
- [ ] Estados definidos: loading / empty / error / success
- [ ] Responsive básico (mobile no roto)
- [ ] Accesible (teclado navegable + contraste base)

### ✅ Performance
- [ ] Sin regresión de Web Vitals (verificado con Lighthouse)
- [ ] Bundle impact medido y documentado en PR

### ✅ Operación
- [ ] Feature flag y rollback path verificados
- [ ] Monitoreo de errores habilitado (Sentry)
- [ ] Documentación corta de decisiones técnicas + changelog
