# Argfy Reengineering — Backlog Jira (Épicas + Historias + AC)

---

## EPIC 1 — Auditoría y baseline técnico-producto
**Objetivo:** Mapear estado actual y definir prioridades de refactor por impacto/riesgo.
**Prioridad:** P0 · **Riesgo:** Bajo · **Esfuerzo:** S · **Dependencias:** Ninguna

### US1.1 Inventario de arquitectura actual
**Como** equipo técnico  
**Quiero** un mapa completo de frontend/backend  
**Para** decidir qué mantener, refactorizar o eliminar

**Acceptance Criteria:**
- [ ] Documento con módulos, dependencias, owners y criticidad
- [ ] Matriz Keep / Refactor / Remove / Merge / Decouple
- [ ] Lista de contratos API críticos
- [ ] Mapa de componentes legacy sin uso

### US1.2 Baseline de UX y performance
**Como** product/design  
**Quiero** métricas baseline de los flujos core  
**Para** medir mejoras reales post-refactor

**Acceptance Criteria:**
- [ ] Flujos core definidos: dashboard, screener, detail, watchlist
- [ ] Métricas baseline: LCP, INP, CLS, errores UI, tiempos de tarea
- [ ] Top 10 fricciones UX documentadas
- [ ] Lighthouse report para homepage + screener + detail

---

## EPIC 2 — Design System v1 (fundación visual)
**Objetivo:** Eliminar inconsistencia visual y acelerar implementación de nuevas features.
**Prioridad:** P0 · **Riesgo:** Bajo · **Esfuerzo:** L · **Dependencias:** Ninguna

### US2.1 Tokens base (dark/light)
**Acceptance Criteria:**
- [ ] Tokens definidos: color, spacing, typography, radius, shadow, transitions
- [ ] Modo dark/light funcional desde CSS custom properties
- [ ] Reglas de uso documentadas en ADR

### US2.2 Componentes fundacionales
**Acceptance Criteria:**
- [ ] Button (3 variantes: primary, secondary, ghost · 3 sizes · loading, disabled, icon)
- [ ] Input (label, error, icon, helperText · focus/error/disabled states)
- [ ] Select (native + custom variants · searchable opcional)
- [ ] Card (3 padding variants · interactive con hover/selected state)
- [ ] Badge (5 variants: default, success, warning, danger, info · dot, removable)
- [ ] Skeleton (4 variants: text, card, table-row, chart)
- [ ] Modal (size variants · closeOnOverlay · portal · open/closing animation)
- [ ] EmptyState (3 variants: default, search, error · icon + title + description + action)
- [ ] ErrorBoundary (fallback UI · onError callback)
- [ ] Tooltip (4 positions · show/hide delay)
- [ ] LoadingSpinner (3 sizes)
- [ ] Accesibilidad base: teclado navegable + contraste mínimo WCAG AA
- [ ] Documentación de props y variantes

### US2.3 Data Table foundation
**Acceptance Criteria:**
- [ ] Table shell reutilizable con header fijo
- [ ] Columnas configurables (key, label, sortable, align, width)
- [ ] Estados: default, empty, error, loading (skeleton)
- [ ] Sort indicator (↕ ↑ ↓)
- [ ] Sticky first column para ticker
- [ ] API de componente documentada

---

## EPIC 3 — Nueva navegación y layout shell
**Objetivo:** Simplificar navegación y jerarquía de información.
**Prioridad:** P0 · **Riesgo:** Medio · **Esfuerzo:** L · **Dependencias:** EPIC 2

### US3.1 App shell unificada
**Acceptance Criteria:**
- [ ] Sidebar collapsible con iconos + labels
- [ ] Menú reducido a áreas core: Screener, Research, Watchlists, Portfolios, Settings
- [ ] Topbar minimal: logo, TickerSearch global, avatar/account, theme toggle
- [ ] 1 MarqueeBar configurable (toggleable, colapsable) — reemplaza los 3 actuales
- [ ] SecondaryNav eliminado
- [ ] Footer minimal (copyright + links legales)
- [ ] Compatible responsive: sidebar → drawer en < lg, tabla scroll horizontal en < md
- [ ] Feature flags: `LAYOUT_V2`, `SIDEBAR_ENABLED`, `MARQUEE_ENABLED`

### US3.2 Homepage v2 (jerarquía visual)
**Acceptance Criteria:**
- [ ] Hero minimal: título + CTA único → Screener
- [ ] Screener Preview: top 5 CEDEARs por PER (live, dinámico)
- [ ] Quick Stats: 4 métricas clave
- [ ] Economic Dashboard colapsado por defecto (toggleable)
- [ ] Secciones estáticas legacy eliminadas (Banks, Government, BCRA, Finances, Markets, Economics, DailyEconomicData)
- [ ] Estados: loading (skeleton), error (retry), empty
- [ ] Feature flag: `HOMEPAGE_V2`

### US3.3 Zustand stores
**Acceptance Criteria:**
- [ ] `authStore`: user, token, tenant, role, isAuthenticated, login, logout
- [ ] `uiStore`: sidebarOpen, theme, commandPaletteOpen, mobileMenuOpen
- [ ] `filterStore`: savedFilters[] con persist middleware
- [ ] AuthContext reemplazado por Zustand (flag `ZUSTAND_AUTH`, convivir 1 semana)
- [ ] Providers.tsx refactorizado: Queries + Zustand + Theme

---

## EPIC 4 — Refactor Screener v2 (core de negocio)
**Objetivo:** Elevar el flujo más crítico del producto a estándar enterprise.
**Prioridad:** P0 · **Riesgo:** Alto · **Esfuerzo:** L · **Dependencias:** EPIC 2 (Table), EPIC 3 (layout)

### US4.1 Tabla virtualizada + performance
**Acceptance Criteria:**
- [ ] Virtualización activa en datasets > 100 rows
- [ ] INP p75 < 200ms (medido vs baseline)
- [ ] Sin bloqueo de UI durante sort/filter
- [ ] Column sorting visual con indicadores (↕ ↑ ↓)
- [ ] Sticky ticker column
- [ ] Feature flag: `SCREENER_V2`

### US4.2 Filtros persistentes y usabilidad
**Acceptance Criteria:**
- [ ] Persistencia local de filtros por usuario (Zustand persist)
- [ ] Saved filters: guardar, cargar, eliminar (múltiples vistas)
- [ ] Feedback visual claro de filtros activos (badges, count)
- [ ] Reset individual por filtro + reset global
- [ ] Mobile filter drawer funcional
- [ ] Feature flag: `SAVED_FILTERS`

### US4.3 Arquitectura de estado limpia
**Acceptance Criteria:**
- [ ] Server state: TanStack Query con staleTimes configurados
- [ ] UI state: Zustand filterStore (persisted)
- [ ] URL search params: filtros activos compartibles via URL
- [ ] Query keys normalizadas
- [ ] API layer unificada (fetch+Zod, sin axios)

### US4.4 Keyboard navigation en screener
**Acceptance Criteria:**
- [ ] ↑↓ navegación entre rows
- [ ] Enter abre detalle del ticker
- [ ] Escape cierra modales/drawers
- [ ] Tab entre filtros
- [ ] Shortcuts visibles en tooltip

---

## EPIC 5 — Limpieza controlada de legacy
**Objetivo:** Reducir deuda técnica sin romper producción.
**Prioridad:** P1 · **Riesgo:** Medio · **Esfuerzo:** M · **Dependencias:** EPIC 1 (auditoría)

### US5.1 Eliminación de componentes y páginas muertas (frontend)
**Acceptance Criteria:**
- [ ] Componentes eliminados: ArgentinaMarquee, GlobalMarquee, TradingViewMarquee, CustomArgentinaMarquee, MarqueeControlPanel, SecondaryNav
- [ ] Dashboard legacy removido (dashboard/Dashboard.tsx, IndicatorModal)
- [ ] Ruta anidada charts/charts/ aplanada
- [ ] @headlessui/react eliminado de dependencias
- [ ] Cero ruptura en rutas activas verificada
- [ ] Changelog de removals documentado

### US5.2 Backend cleanup acotado
**Acceptance Criteria:**
- [ ] Routers muertos eliminados: expanded_indicators, unified_economic, data, economic_cards
- [ ] Schedulers consolidados: UnifiedScheduler eliminado, tasks migradas a APScheduler
- [ ] Endpoints duplicados en admin router limpiados
- [ ] Servicios no usados eliminados: dollar_multi_source, http_factory, bcra_massive, bcra_httpx
- [ ] Contratos API críticos intactos (fundamentals, auth, billing)
- [ ] tests/ de ratio engine agregados (PER, ROE5y, CAGR, Deuda/EBITDA)

---

## EPIC 6 — Premium experience
**Objetivo:** Experiencia profesional diferenciadora tipo TIKR/Koyfin.
**Prioridad:** P1 · **Riesgo:** Bajo · **Esfuerzo:** L · **Dependencias:** EPIC 2 (DS), EPIC 3 (layout)

### US6.1 Command palette (⌘K)
**Acceptance Criteria:**
- [ ] ⌘K / Ctrl+K abre palette
- [ ] Fuzzy search: tickers, páginas, acciones rápidas
- [ ] Navegación por teclado (↑↓, Enter, Escape)
- [ ] Resultados agrupados (Tickers, Páginas, Acciones)
- [ ] Documentación de shortcuts visible

### US6.2 Microinteracciones y feedback
**Acceptance Criteria:**
- [ ] Transiciones suaves en: sidebar open/close, modal open/close, tabs switch
- [ ] Skeletons en todos los flujos core (screener, detail, dashboard)
- [ ] Error handling accionable: retry button, guidance text, empty state
- [ ] Toast notifications para acciones (save filter, export CSV, error)

### US6.3 Ticker detail v2 (Research)
**Acceptance Criteria:**
- [ ] TickerHeader: nombre, ticker, precio, cambio %, exchange, sector
- [ ] KeyMetrics: 6 tarjetas con métricas clave (PER, ROE, Margen, D/E, FCF, Payout)
- [ ] PriceChart: 5y interactive con period selector (1m, 6m, 1y, 5y, max)
- [ ] MetricHistoryChart: selector de métrica con histórico trimestral
- [ ] FinancialTable: revenue, net income, EBITDA, FCF por trimestre
- [ ] CompanyProfile: sector, industry, country, source data
- [ ] Feature flag: `DETAIL_V2`

---

## EPIC 7 — Observabilidad, QA y rollout seguro
**Objetivo:** Asegurar estabilidad durante toda la migración.
**Prioridad:** P0 · **Riesgo:** Alto · **Esfuerzo:** M · **Dependencias:** Ninguna

### US7.1 Feature flags por módulo
**Acceptance Criteria:**
- [ ] Flags implementadas: `RATE_LIMIT_ENABLED`, `LAYOUT_V2`, `SIDEBAR_ENABLED`, `MARQUEE_ENABLED`, `HOMEPAGE_V2`, `ZUSTAND_AUTH`, `SCREENER_V2`, `SAVED_FILTERS`, `DETAIL_V2`
- [ ] Rollback operativo < 15 min por flag
- [ ] Playbook de incidente documentado
- [ ] Flag runtime vs compile-time decidido por módulo

### US7.2 Cobertura de flujos críticos
**Acceptance Criteria:**
- [ ] Smoke tests en: auth (login, register, google), screener (load, filter, sort, paginate, export), ticker detail (load, price chart, metric history)
- [ ] Umbral mínimo 80% de flujos core cubiertos
- [ ] Gate básico para release: smoke tests pass + 0 P1 blockers
- [ ] Sentry configurado en frontend + backend con alertas

### US7.3 API layer unificada
**Acceptance Criteria:**
- [ ] Single API client con fetch + Zod validation (sin axios)
- [ ] Auth interceptor (JWT + API key fallback)
- [ ] Error handling tipado con errores específicos por dominio
- [ ] Hooks legacy migrados a TanStack Query (useIndicators, useBCRAReal, etc.)

---

## EPIC 8 — Convenciones y estructura final del repositorio
**Objetivo:** Estandarizar para escalar el equipo y el producto.
**Prioridad:** P2 · **Riesgo:** Bajo · **Esfuerzo:** S · **Dependencias:** EPIC 1 (auditoría)

### US8.1 Estructura target frontend
**Acceptance Criteria:**
- [ ] Árbol final acordado y documentado
- [ ] Domain boundaries definidos: ui/, layout/, screener/, research/, dashboard/, shared/
- [ ] Convenciones de naming/imports aplicadas
- [ ] components/index.tsx spliteado en archivos individuales

### US8.2 ADRs y guía de contribución
**Acceptance Criteria:**
- [ ] ADRs para decisiones clave: Zustand vs RTK, fetch+Zod vs axios, feature-based folders, state architecture
- [ ] Guía de patrones: state management, data fetching, UI components, error handling, loading states
- [ ] Checklist de PR con criterios de calidad
- [ ] README actualizado con arquitectura objetivo

---

## Backlog priorizado por sprint

### Sprint 1 (Día 0-5): Foundation
| Issue | Tipo | Prioridad | Esfuerzo |
|---|---|---|---|
| US1.1 Inventario arquitectura | Tech Debt | P0 | S |
| US1.2 Baseline UX/performance | Tech Debt | P0 | S |
| US7.1 Feature flags | Tech Debt | P0 | M |
| US7.2 Smoke tests core | Tech Debt | P0 | M |
| US5.1 Eliminar legacy frontend (muertos) | Tech Debt | P1 | S |
| US5.2 Backend cleanup (fixes inmediatos) | Tech Debt | P0 | S |

### Sprint 2 (Día 5-12): Design System v1
| Issue | Tipo | Prioridad | Esfuerzo |
|---|---|---|---|
| US2.1 Tokens base | Feature | P0 | S |
| US2.2 Componentes fundacionales | Feature | P0 | L |
| US2.3 Data Table foundation | Feature | P0 | M |
| US7.3 API layer unificada | Tech Debt | P1 | M |
| US5.1 Resto de limpieza frontend | Tech Debt | P1 | S |

### Sprint 3 (Día 12-19): Layout + Navigation
| Issue | Tipo | Prioridad | Esfuerzo |
|---|---|---|---|
| US3.1 App shell unificada | Feature | P0 | L |
| US3.2 Homepage v2 | Feature | P1 | M |
| US3.3 Zustand stores | Tech Debt | P1 | M |

### Sprint 4 (Día 19-26): Screener v2
| Issue | Tipo | Prioridad | Esfuerzo |
|---|---|---|---|
| US4.1 Tabla virtualizada | Feature | P0 | M |
| US4.2 Filtros persistentes | Feature | P1 | M |
| US4.3 Arquitectura estado limpia | Tech Debt | P1 | M |
| US4.4 Keyboard navigation | Feature | P2 | S |

### Sprint 5 (Día 26-33): Research + Backend
| Issue | Tipo | Prioridad | Esfuerzo |
|---|---|---|---|
| US6.3 Ticker detail v2 | Feature | P1 | L |
| US5.2 Backend cleanup (routers + schedulers) | Tech Debt | P1 | M |

### Sprint 6 (Día 33-40): Premium Polish
| Issue | Tipo | Prioridad | Esfuerzo |
|---|---|---|---|
| US6.1 Command palette | Feature | P2 | M |
| US6.2 Microinteracciones | Feature | P2 | M |
| US8.1 Estructura target | Tech Debt | P2 | S |
| US8.2 ADRs + guía | Tech Debt | P2 | S |

---

## Plantilla de issue Jira

```
Título: [ARGFY-REF] <módulo> — <resultado esperado>

Descripción breve:
<Qué problema resuelve y por qué importa al negocio>

Contexto técnico:
<Arquitectura actual, archivos involucrados, dependencias>

Tipo: Story / Task / Tech Debt
Prioridad: P0 / P1 / P2
Riesgo: Bajo / Medio / Alto
Esfuerzo: S / M / L
Feature Flag: <nombre_flag>

Dependencias:
- Bloqueante de: <issue-keys>
- Bloqueado por: <issue-keys>

Acceptance Criteria:
- [ ] <criterio funcional>
- [ ] <criterio técnico>
- [ ] <criterio UX>
- [ ] <criterio performance>
- [ ] Sin regresión en flujos core (auth, billing, screener, detail)

Definition of Done:
- [ ] Funcional en entorno target
- [ ] Sin regresión en flujos core
- [ ] Métrica before/after adjunta
- [ ] Feature flag + rollback definidos
- [ ] Documentación mínima actualizada
- [ ] PR < 300 líneas

Rollback Plan:
<Cómo revertir este cambio en < 15 min>
```
