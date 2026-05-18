# Plan de Fork de Coolify — WebsHooks Platform

> **Fecha:** 2026-05-17
> **Autor:** Federico Monfasani
> **Estado:** Draft inicial
> **Documentos relacionados:**
>
> - [`plan_saneamiento.md`](./plan_saneamiento.md) — qué hay verde hoy
> - [`plan_devops_vps_opencode.md`](./plan_devops_vps_opencode.md) — norte de infra
>
> **Alcance:** Forkear Coolify v4 para convertirlo en la base de una plataforma propia tipo Vercel/Railway, adaptada al modelo SCRUM de WebsHooks. Cubre corto, mediano y largo plazo.

---

## 0. Por qué forkear y no usar vanilla

Hoy Coolify v4 nos resuelve el 80% de lo que necesitamos pero choca con cinco limitaciones que no son configurables:

1. **RBAC solo a nivel team**, no proyecto → fuerza el workaround "1 team por colaborador".
2. **Una sola pending invitation por email** entre todos los teams → bloquea el SCRUM cruzado de 16 invitaciones.
3. **API pública limitada** (solo `projects` CRUD) → no podemos automatizar setup ni hacer GitOps.
4. **Sin eventos estandarizados de deploy** → no se puede enchufar observabilidad ni notificaciones sin tocar core.
5. **Sin audit log** → ningún rastro de quién deployó qué (mata accountability SCRUM).

Las tres primeras son **bloqueos de modelo de datos / auth**: no se resuelven con plugins externos ni con sidecars. Eso solo justifica un fork; el resto se puede atacar con webhooks y cron.

**Principio rector**: forkear **solo lo que toca core o modelo de datos**. Todo lo demás se hace con automation externa que conversa con la API forkeada.

---

## 1. Visión norte — "Vercel self-hosted, tropicalizado"

Llegar a una plataforma donde:

- **Git push → deploy** en cualquier vertical (ecommerce, SaaS, blog) sin tocar YAML.
- **Cada colaborador es Admin de lo suyo** y Member de los demás, sin teams ni invitaciones cruzadas.
- **Preview deployments por PR** con dominio efímero (`pr-123.electronica.webshooks.com`).
- **Templates verticales versionados** (`@webshooks/ecommerce-base`, `@webshooks/blog-base`) que un colaborador instancia con un click.
- **Observabilidad nativa** (logs estructurados, métricas, tracing) sin pegar Grafana con cinta.
- **API-first**: todo lo que se hace por UI es callable por CLI y SDK.
- **Multi-VPS** cuando un solo Hetzner CX43 no alcance.
- **White-label**: cuando un colaborador se vaya a montar su propio negocio, puede llevarse el panel con su branding.

Métrica de éxito a 12 meses: **un nuevo colaborador entra al equipo y deploya su primera tienda en menos de 1 hora sin pedir ayuda**.

---

## 2. Arquitectura objetivo (plano lógico)

```
┌─────────────────────────────────────────────────────────────────┐
│                       Edge plane                                │
│  Cloudflare DNS + CDN + WAF (gratis, ya tenemos)                │
│  (futuro: Workers para edge functions)                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                       Control plane                             │
│  Coolify-fork (Laravel) — UI, API, RBAC, audit log, templates   │
│  Postgres-control (state)                                       │
│  Redis (queues, sessions)                                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                       Data plane                                │
│  Docker + Traefik (workloads de colaboradores y argfy)          │
│  Por proyecto: api + web + db + cron                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    Observability plane                          │
│  Loki (logs) + Prometheus (métricas) + Grafana (dashboards)     │
│  Sentry (errores app)                                           │
└─────────────────────────────────────────────────────────────────┘

         Storage plane: S3-compatible (Backblaze B2 o R2) para
         backups Postgres y volúmenes Docker
```

Hoy tenemos sólo el control plane + data plane corriendo en un solo Hetzner. El resto se va agregando por fase.

---

## 3. Higiene del fork (Fase 0 — pre-requisito a todo)

| #   | Acción                                                                         | Por qué                                                  |
| --- | ------------------------------------------------------------------------------- | --------------------------------------------------------- |
| 0.1 | Fork de `coollabsio/coolify` a `webshooks-org/coolify` en GitHub            | Punto de partida                                          |
| 0.2 | Branch `webshooks/main` que rebasea upstream **semanalmente**           | Cuanto más esperás, peor el merge                       |
| 0.3 | `WEBSHOOKS_CHANGES.md` en root con cada PR forkeado y su intent               | Saber qué es nuestro cuando rompa                        |
| 0.4 | Feature flags (`config('webshooks.feature.x')`) en cada cambio                | Apagar sin revertir                                       |
| 0.5 | Migraciones DB en namespace `webshooks_*`                                     | No chocar con upstream                                    |
| 0.6 | CI: tests upstream + tests propios                                              | Detectar drift temprano                                   |
| 0.7 | Docker image propia `ghcr.io/webshooks-org/coolify:vX.Y.Z`                    | No depender de coollabs registry                          |
| 0.8 | Doc `CONTRIBUTING.md` con regla "PR upstream-first si el cambio es genérico" | Reducir deuda — contribuir al original si aplica a todos |

**Salida**: fork compilable y deployable, sin cambios funcionales todavía. **Tiempo estimado: 3 días.**

---

## 4. FASE 1 — Corto plazo (semanas 1-4, hasta 2026-06-15)

> Norte de la fase: **desbloquear el modelo SCRUM y dejar la API utilizable para automation.**

### 4.1 Fix del invitation flow [BLOQUEANTE HOY]

Permitir múltiples invitaciones pendientes para el mismo email, scoped al team.

- Lift de la unique constraint global en `team_invitations.email`
- Magic link único que acepta todas las pendientes en un click
- Endpoint `POST /api/v1/invitations/bulk` (1 llamada, N invites)
- Feature flag: `webshooks.feature.multi_pending_invitations`

**Impacto**: las 16 invitaciones del SCRUM en una sola operación. Hoy son 16 clicks + coordinación humana.

### 4.2 API REST expansion

Convertir las Actions Livewire internas en endpoints REST públicos con scopes.

- `POST/PATCH/DELETE /api/v1/teams`
- `POST /api/v1/teams/{id}/members` (add/remove)
- `GET/POST/PUT/DELETE /api/v1/services/{id}/env` (env vars CRUD)
- `POST /api/v1/projects/bulk`
- Tokens con scopes (`teams:write`, `deploy:trigger`, `env:read`, etc.)
- OpenAPI 3.1 spec autogenerado

**Impacto**: GitOps + CLI declarativo + automation externa sin DB-poking.

### 4.3 Project templates con placeholders

Hoy los templates son solo "Docker images del marketplace". Queremos templates full-stack:

- Subir `coolify-template.yml` con placeholders `{proyecto}`, `{dominio}`, `{tema}`
- UI: "New project from template" prompt los valores y sustituye en build time
- Template registry interno (`webshooks/ecommerce-base`, `webshooks/blog-base`)
- Versionado semántico (`@1.2.0`)

**Impacto**: onboarding de un nuevo colaborador pasa de 30 minutos de `sed` a 1 click.

### 4.4 Webhook bus estandarizado

Emitir eventos firmados con HMAC para hooking externo:

- `deploy.started`, `deploy.succeeded`, `deploy.failed`
- `healthcheck.failed`, `healthcheck.recovered`
- `service.created`, `service.deleted`
- `member.added`, `member.removed`
- Configurable por team y globalmente
- Retry con backoff exponencial, dead-letter queue

**Impacto**: enchufar Sentry/Slack/Discord/Loki sin tocar core.

### 4.5 Audit log

Tabla `webshooks_audit_events(actor_id, action, resource_type, resource_id, payload_json, ip, ua, ts)`.

- Visible por team en la UI
- Filtrable + exportable a CSV/JSON
- Retención 90 días por defecto

**Impacto**: SCRUM accountability + debugging post-mortem.

### 4.6 Resource quotas por team

- CPU / RAM / disk caps por team configurables por el Owner
- UI muestra uso actual vs cap
- Alerta cuando >80%

**Impacto**: un colaborador no puede tirar el VPS de los otros.

### Salida de Fase 1

- Fork desplegado en `coolify.webshooks.com`
- Las 16 invitaciones SCRUM hechas con 1 comando CLI
- 4 colaboradores con audit log de sus deploys
- API REST funcional → arranca el CLI

---

## 5. FASE 2 — Mediano plazo (meses 2-3, hasta 2026-08-31)

> Norte de la fase: **convertir Coolify-fork en plataforma operable por equipo, no por una persona.**

### 5.1 Project-level RBAC (el cambio más invasivo)

Hoy: roles solo a nivel team. Mañana: tabla `webshooks_project_members(project_id, user_id, role)` con middleware que checkea team-role O project-role.

**Beneficio**: pasamos de "1 team por colaborador + 16 invitaciones" a "1 team WebsHooks + 4 proyectos + members directos". Modelo SCRUM nativo.

**Costo**: 2-3 semanas. Toca middleware, UI, migraciones, todos los `PolicyGate` de Laravel.

**Plan**: feature flag, double-write durante 1 mes, deprecar el modelo viejo después.

### 5.2 CLI declarativo `wshctl`

Repo separado: `webshooks-org/wshctl` en Go.

```bash
wshctl apply -f team.yaml   # idempotente
wshctl logs ws-electronica/api --tail 100
wshctl deploy ws-tienda
wshctl rollback ws-zapateria --to=v1.2.3
```

YAML declarativo (estilo Kubernetes):

```yaml
apiVersion: webshooks.io/v1
kind: Project
metadata:
  name: ws-electronica
  team: webshooks
spec:
  template: ecommerce-base@1.2.0
  domain: electronica.webshooks.com
  members:
    - { user: joaquin@..., role: admin }
    - { user: mateo@..., role: member }
  env:
    POSTGRES_DB: electronica
    SENTRY_DSN: { fromSecret: sentry-electronica }
```

**Impacto**: el estado del VPS se reproduce desde git. Onboarding de un VPS nuevo = 1 comando.

### 5.3 Preview deployments por PR

Webhook de GitHub → Coolify crea un ambiente efímero por PR.

- Dominio auto: `pr-{n}.{proyecto}.webshooks.com`
- DB clonada (snapshot del seed)
- Auto-destrucción al cerrar el PR
- Comment en el PR con el link

**Impacto**: review visual real. Killer feature de Vercel — sin esto no es comparable.

### 5.4 Build cache global

- Cache de Docker layers compartido entre proyectos del mismo template
- Cache de `node_modules` / `vendor` por proyecto (S3-backed)
- Reduce build time de ~3 min a ~30 seg

### 5.5 Backups automáticos + restore one-click

- Postgres → S3 (Backblaze B2) cada hora con WAL archiving
- Snapshots de volúmenes Docker semanales
- UI: "Restore to point in time" con timeline visual
- Test de restore automatizado (cron weekly: restaurar a un VPS de staging, run smoke tests)

### 5.6 Observability plane nativo

- Loki para logs (push directo desde containers via Docker driver)
- Prometheus para métricas (node-exporter + cAdvisor + app metrics)
- Grafana embebido en la UI de Coolify (iframe en cada proyecto)
- Dashboards prebuilt por template

### 5.7 Multi-VPS / multi-region

- Agregar un Hetzner FSN2 como segundo nodo
- Coolify-fork distribuye workloads (round-robin, o por affinity)
- Postgres con read replicas en el segundo nodo
- DNS geo-routing via Cloudflare

**Cuándo activar**: cuando el CX43 actual pase 70% CPU sostenido o cuando un colaborador escale a producción real.

### 5.8 Notifications hub

- Integraciones nativas: Discord, Slack, Telegram, Email, WhatsApp (Twilio)
- Routing rules por evento + team + severidad
- Quiet hours (no pingear a las 3am salvo crítico)

### Salida de Fase 2

- Project-level RBAC en prod
- `wshctl apply` reproduce todo el VPS desde git
- Preview deployments funcionando
- Backups en B2 con restore probado
- Loki/Prometheus/Grafana integrados
- Capacidad de escalar a 2do VPS

---

## 6. FASE 3 — Largo plazo (meses 4-12, hasta 2027-05-17)

> Norte de la fase: **paridad con Vercel/Railway en features visibles + features propios que ellos no tienen.**

### 6.1 Edge compute

- Cloudflare Workers para functions (Hono/itty-router)
- Edge config (KV) gestionado desde el panel
- Image optimization API (`/cdn-cgi/image/...` o propio Sharp service)
- A/B testing en edge

### 6.2 Serverless functions nativas

- `webshooks-fn` runtime (Bun + Hono) en data plane
- Deploy de funciones independientes del compose principal
- Cold start <100ms

### 6.3 KV store / Edge config

- Redis-backed key-value para feature flags, A/B, config dinámico
- API + UI + SDK

### 6.4 Cron jobs nativos

- UI para schedular jobs (`@hourly`, `@daily`, cron syntax)
- Logs por ejecución, retries, alertas si falla
- Sustituye los `*_cron` containers manuales actuales

### 6.5 Analytics built-in

- Page views, latency p50/p95/p99, error rate, RUM
- Métricas por proyecto, expuestas al Admin de ese proyecto
- Sin third-party tracker — privacy-first

### 6.6 Marketplace de templates verticales

- `@webshooks/ecommerce-base`, `@webshooks/blog-base`, `@webshooks/saas-starter`
- Cada template versionado, con migraciones automáticas
- Templates de terceros publicables (revenue share futuro)

### 6.7 White-label / branding por team

- Cada team puede configurar logo, colores, dominio del panel
- Subdominio `panel.{cliente}.com` con CNAME a `coolify.webshooks.com`
- Cuando un colaborador se va a montar lo suyo, se lleva el panel

### 6.8 Billing & metering

- Track de CPU·hora, RAM·hora, GB egress, GB storage por team
- Plans (Free, Pro, Scale) configurables
- Integración Mercado Pago + Stripe
- Invoice generation

### 6.9 SSO / SAML enterprise

- Google Workspace, GitHub, Microsoft Entra, custom SAML
- Para cuando un colaborador entre a una empresa que ya tenga IDP corporativo

### 6.10 AI-assisted ops

- Logs → diagnóstico automático ("tu build falló porque X, sugerencia Y")
- Anomaly detection en métricas
- Suggested env vars por template (Claude API o local Llama)

### 6.11 Compliance reports

- SOC2-lite report autogenerado por team
- PCI checklist para proyectos ecommerce
- LGPD / Argentina Ley 25.326 — data residency report

### 6.12 Public API marketplace

- Apps de terceros que se conectan via OAuth
- Webhooks bidireccionales
- Revenue share con devs

### Salida de Fase 3

WebsHooks Platform compite con Vercel en demos de Argentina con ventajas:

- Self-hosted opcional (Vercel no lo ofrece)
- Templates verticales (Vercel es genérico)
- Pricing en pesos
- Soporte en español
- White-label para reseller

---

## 7. Tabla maestra de iniciativas

Prioridad: **P0** = bloqueante deadline 2026-05-22, **P1** = Fase 1, **P2** = Fase 2, **P3** = Fase 3.

| Iniciativa                    | Fase | Prio | Esfuerzo | Dependencias                  |
| ----------------------------- | ---- | ---- | -------- | ----------------------------- |
| Fork setup + higiene          | 0    | P0   | 3d       | —                            |
| Fix multi-pending invitations | 1    | P0   | 2d       | Fork setup                    |
| API REST expansion            | 1    | P1   | 2sem     | Fork setup                    |
| Project templates             | 1    | P1   | 1sem     | API REST                      |
| Webhook bus                   | 1    | P1   | 1sem     | API REST                      |
| Audit log                     | 1    | P1   | 4d       | —                            |
| Resource quotas               | 1    | P1   | 1sem     | —                            |
| Project-level RBAC            | 2    | P2   | 3sem     | API REST                      |
| `wshctl` CLI                | 2    | P2   | 2sem     | API REST completa             |
| Preview deployments           | 2    | P2   | 2sem     | Templates + Webhook bus       |
| Build cache                   | 2    | P2   | 1sem     | Storage S3                    |
| Backups + restore UI          | 2    | P2   | 2sem     | Storage S3                    |
| Observability plane           | 2    | P2   | 3sem     | —                            |
| Multi-VPS                     | 2    | P2   | 4sem     | Observability                 |
| Notifications hub             | 2    | P2   | 1sem     | Webhook bus                   |
| Edge compute                  | 3    | P3   | 6sem     | Cloudflare Workers POC        |
| Serverless functions          | 3    | P3   | 8sem     | Data plane multi-tenant       |
| KV store                      | 3    | P3   | 2sem     | Redis cluster                 |
| Cron nativos                  | 3    | P3   | 1sem     | —                            |
| Analytics                     | 3    | P3   | 4sem     | Observability                 |
| Marketplace templates         | 3    | P3   | 6sem     | Templates v1 + Billing        |
| White-label                   | 3    | P3   | 3sem     | RBAC project-level            |
| Billing                       | 3    | P3   | 8sem     | Resource quotas               |
| SSO SAML                      | 3    | P3   | 2sem     | —                            |
| AI ops                        | 3    | P3   | 4sem     | Observability + Anthropic API |
| Compliance reports            | 3    | P3   | 4sem     | Audit log + Billing           |
| API marketplace               | 3    | P3   | 8sem     | API REST + Billing            |

---

## 8. Stack técnico del fork

Lo que **mantenemos** de upstream Coolify:

- Laravel 11 + Livewire 3 (UI)
- Postgres como state store
- Redis para queues
- Docker + Traefik en data plane
- Stripe billing skeleton (que ya tiene)

Lo que **agregamos**:

- `wshctl` CLI en Go (binario único, cross-compile)
- Webhook relay service en Bun + Hono (para eventos high-throughput)
- Loki + Promtail + Grafana en data plane (docker-compose aparte)
- Backblaze B2 SDK para storage layer
- Anthropic SDK (Claude Opus 4.7 / Haiku 4.5) para AI features

Lo que **descartamos** (por ahora):

- Reescritura del frontend a SPA — Livewire alcanza
- Kubernetes — Docker Swarm o Nomad solo si pasamos 5+ VPS
- gRPC — REST + webhooks alcanzan

---

## 9. Riesgos y mitigaciones

| Riesgo                                            | Probabilidad | Impacto  | Mitigación                                                                      |
| ------------------------------------------------- | ------------ | -------- | -------------------------------------------------------------------------------- |
| Merge conflicts con upstream                      | Alta         | Medio    | Rebase semanal, feature flags, CI                                                |
| Coolify pivotea a v5 incompatible                 | Media        | Alto     | Documentar diffs, contribuir upstream-first cuando aplique                       |
| Performance del control plane con 50+ proyectos   | Media        | Alto     | Profiling temprano, Redis cache, query optimization                              |
| Vendor lock-in con Backblaze B2                   | Baja         | Bajo     | Abstracción S3-compatible — swap a R2/Wasabi sin cambio de código             |
| 1 dev (Federico) bus factor                       | Alta         | Crítico | Documentar todo, onboarding doc, los colaboradores empiezan a contribuir al fork |
| Costos de Cloudflare Workers al escalar           | Baja         | Medio    | Free tier alcanza hasta 100k req/día por worker — replantear cuando lleguemos  |
| Coolify upstream agrega features que ya forkeamos | Media        | Bajo     | Bueno: borramos nuestro código y usamos el upstream                             |

---

## 10. Métricas de éxito

| Métrica                               | Hoy    | Fin Fase 1 | Fin Fase 2         | Fin Fase 3 |
| -------------------------------------- | ------ | ---------- | ------------------ | ---------- |
| Tiempo de onboarding nuevo colaborador | 2h+    | 30min      | 10min              | <5min      |
| Deploy en producción (tiempo)         | 3-5min | 3-5min     | 1-2min (con cache) | <1min      |
| Manual steps post-deploy               | 4-5    | 1          | 0                  | 0          |
| Proyectos manejados por 1 admin        | 5      | 20         | 50                 | 200+       |
| Cobertura de tests del fork            | 0%     | 40%        | 70%                | 85%        |
| Endpoints API documentados             | ~10    | 50         | 100+               | 150+       |
| Uptime ofrecido                        | 99%    | 99.5%      | 99.9%              | 99.95%     |
| Time to recovery (incidente)           | 1-2h   | 30min      | 10min              | 5min       |

---

## 11. Próximas 5 acciones concretas (esta semana)

1. **Hoy 2026-05-17**: terminar el saneamiento (Fase 0 de `plan_saneamiento.md`) — sin esto no se forkea nada.
2. **2026-05-22**: cerrar deadline WebsHooks Consigna 4.0 con Coolify vanilla, modelo SCRUM secuenciado.
3. **2026-05-23**: crear repo `webshooks-org/coolify` (fork), montar CI básica, primer build local.
4. **2026-05-25**: implementar Fix 4.1 (multi-pending invitations) — primer PR del fork, demuestra el flujo end-to-end.
5. **2026-06-01**: poner `coolify.webshooks.com` apuntando al fork (no al upstream). Cutover testeado en staging primero.

---

## 12. Decisiones abiertas (a resolver antes de Fase 1)

- [ ] ¿Repo del fork público o privado? (Público invita contribuciones, privado nos da margen para pivots no anunciados)
- [ ] ¿Contribuir upstream las features genéricas (multi-pending, audit log) o quedárnoslas? Mi voto: **upstream-first todo lo que sea claramente bug fix o feature genérica**, fork lo que sea opinionated o de negocio.
- [ ] ¿Llamamos al producto "Coolify-WebsHooks" o le ponemos nombre propio (e.g. "Hangar", "Despliegue", "Plataforma X")? Si pensamos vender white-label, mejor nombre propio.
- [ ] ¿Pricing target del producto? Define qué features son free vs paid en Fase 3.
- [ ] ¿Qué hacemos con el `coolify.webshooks.com` actual durante el cutover? Mantener vanilla en paralelo en `legacy.coolify.webshooks.com` 30 días.

---

## Apéndice A — Comparación con alternativas

| Plataforma                   | Pros                     | Contras                             | Por qué no la usamos      |
| ---------------------------- | ------------------------ | ----------------------------------- | -------------------------- |
| **Vercel**             | Gold standard UX         | $$$, vendor lock-in, no self-host | Costo, soberanía de datos |
| **Railway**            | Buen DX, pricing decente | No self-host, US-only               | Self-host es requisito     |
| **Render**             | Maduro                   | $$$, no self-host                 | Costo                      |
| **Dokku**              | OSS, simple              | UX vieja, no multi-tenant           | UX                         |
| **CapRover**           | OSS, Docker-based        | Roadmap lento                       | Roadmap lento              |
| **Caprover**           | Igual al anterior        | —                                  | —                         |
| **Coolify vanilla**    | OSS, moderno, activo     | Las 5 limitaciones de §0           | Por eso forkeamos          |
| **Build from scratch** | Control total            | 2-3 años de trabajo                | Time to market             |

Conclusión: forkear Coolify es el **mejor punto de partida** dado time-to-market y madurez del core. Construir desde cero solo tendría sentido si las limitaciones fueran arquitecturales (no lo son).

---

## Apéndice B — Convención de nombres post-fork

- Org GitHub: `webshooks-org`
- Repo fork: `webshooks-org/coolify` (branch `webshooks/main`)
- CLI: `webshooks-org/wshctl`
- Templates: `webshooks-org/template-{vertical}` (e.g. `template-ecommerce`)
- Docker registry: `ghcr.io/webshooks-org/*`
- Dominio panel: `coolify.webshooks.com` (durante cutover: `legacy.coolify.webshooks.com` para vanilla)
- Subdominio público de marca (cuando exista nombre propio): a definir

---

> **Próximo paso real**: terminar Fase 0 del `plan_saneamiento.md` (deadline 2026-05-22). Después de eso, primer commit del fork.
