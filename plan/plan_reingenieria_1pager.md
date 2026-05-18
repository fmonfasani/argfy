# Argfy Reengineering Program — Executive One-Pager

## Objetivo
Transformar Argfy en una plataforma financiera premium, enterprise y escalable en 90 días, sin rewrite y sin comprometer operación productiva.

## Contexto
Argfy ya funciona en producción — backend, DB schema, auth, billing, APIs y deploy están operativos. La deuda principal está en el frontend: UX/UI inconsistente, arquitectura confusa, componentes legacy, navegación saturada y baja jerarquía visual.

**Calificación actual:** Backend 7.5/10 · Frontend 4.5/10 · UX/UI 3/10

## Estrategia
Reingeniería incremental por fases con feature flags, rollback rápido y releases controlados:

| Fase | Timeline | Entregas clave | KPIs |
|---|---|---|---|
| **Foundation + Quick Wins** | Días 0–30 | Fix rate limiter, feature gates, seed plans. Design System v1 (tokens + 13 componentes). Nueva navegación (sidebar + topbar minimal). Homepage limpia (de 10 secciones a 3). | LCP < 3.0s · 0 incidentes P1 · -40% clutter visual |
| **Core Product Refactor** | Días 31–60 | Screener v2 (tabla virtualizada + filtros persistentes). API layer unificada (sin axios). Backend cleanup (routers muertos, schedulers duplicados). | -30% tiempo de screener · INP < 200ms · Legacy reducido 30% |
| **Scale + Premium Polish** | Días 61–90 | Command palette (⌘K). Keyboard navigation global. Performance audit. Light mode. Deuda legacy -50%. Documentación final. | LCP < 2.5s · CLS < 0.1 · Bundle -30% · Cobertura tests ≥ 80% |

## Qué se preserva sí o sí
- Backend y contratos API
- Lógica financiera (screener, métricas, modelos)
- Auth, billing, deploy e infraestructura

## Qué se mejora
- **Arquitectura frontend:** feature-based/domain-driven, separation of concerns
- **Design System:** tokens + componentes + dark/light + accesibilidad
- **UX core:** dashboard, screener, tables, navegación, estados vacío/error/loading
- **Performance:** LCP/INP/CLS, bundle size, virtualización de tablas
- **DX:** naming consistente, boundaries claros, convenciones documentadas

## KPIs de éxito (90 días)
| Métrica | Baseline | Meta 90d |
|---|---|---|
| LCP (p75) | ~4.0s | < 2.5s |
| INP (p75) | ~300ms | < 200ms |
| CLS (p75) | ~0.3 | < 0.1 |
| JS Bundle inicial | ~250KB | < 160KB |
| Task success en screener | baseline | +20% |
| Tiempo de tareas clave | ~45s | -30% |
| Errores frontend / 1k sesiones | ~20 | < 10 |
| Legacy crítico eliminado | — | -50% |
| Incidentes P1 por refactor | — | **0** |

## Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| Regresión funcional en flujos críticos | Feature flags por módulo. Smoke tests core. Rollback < 15 min. |
| Alcance excesivo (scope creep) | Priorización ROI/riesgo. Control quincenal de backlog. Demo cada 2 semanas. |
| Deuda oculta en legacy no detectada | Auditoría inicial con mapa Keep/Refactor/Remove. Deprecación progresiva con warning de 1 semana. |
| Dependencias externas (Coolify, APIs) | Backlog independiente del fork de Coolify. APIs financieras ya integradas. |

## Resultado esperado
En 90 días, Argfy pasa de **"producto funcional con deuda"** a **"base enterprise escalable"** — mejorando percepción premium, velocidad de ejecución y capacidad de crecimiento sin interrumpir el negocio.

## Cadencia operativa
- **Weekly Steering** (60 min): estado por fase, riesgos, decisiones
- **Demo Quincenal** (30 min): vertical slices en staging/prod-flagged
- **Release semanal** o bisemanal, siempre con flags
- **Regla de oro:** si no es reversible en 15 minutos, no sale a producción
