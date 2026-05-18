# Guía DevOps — Ecosistema webshooks.com + Proyectos en VPS Hetzner

> **Fecha:** 2026-05-17
> **VPS:** Hetzner CX43 (4 vCPU · 16GB RAM · 160GB NVMe)
> **Orquestador:** Coolify + Docker Compose
> **Proxy:** Traefik + Cloudflare
> **Stack base:** FastAPI + Next.js (por proyecto, libre)

---

> **Nota:** Esta guía fue revisada por un arquitecto DevOps senior. Las críticas y correcciones están incorporadas en cada sección. La sección [23](#23-correcciones-post-review) resume los cambios aplicados.

---

## 1. Visión General

Esta guía define la arquitectura DevOps definitiva para el ecosistema **webshooks.com** y todos los proyectos que conviven en un mismo VPS. Está diseñada para ser operada por un equipo pequeño (~4 colaboradores) y escalar ordenadamente sin sobredimensionar.

### Ecosistema completo

```
webshooks.com (plataforma principal — control plane)
├── tienda.webshooks.com        (demo ecommerce)
├── electronica.webshooks.com   (demo electronica)
├── zapateria.webshooks.com     (demo zapateria)
├── clinica.webshooks.com       (demo clinica)
├── instructor.webshooks.com    (demo instructor)
├── yoga.webshooks.com          (demo yoga)
└── entrenador.webshooks.com    (demo personal trainer)

projects/ (proyectos independientes, NO bajo webshooks)
├── argfy.com                   (plataforma financiera)
├── luzguffantti.com            (portfolio freelance)
└── anamurat.com                (portfolio freelance)
```

### Decisiones arquitectónicas clave

| Decisión | Opción elegida | Motivo |
|----------|---------------|--------|
| DB por demo | 1 Postgres compartido (pg-demos), 1 database por demo | Eficiencia RAM vs aislamiento |
| webshooks stack | FastAPI + Next.js | Mismo stack que argfy, expertise compartida |
| webshooks rol | Panel de control — **no** API gateway | Cada demo es independiente en su subdominio |
| Stack por proyecto | Libre (cada proyecto define su Dockerfile) | Sin restricciones técnicas |
| Repositorios | 1 repo por proyecto | Independencia total |
| DB multi-tenant | webshooks y argfy: schemas separados por tenant | Aislamiento lógico dentro de misma DB |

---

## 2. Arquitectura General

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                             CLOUDFLARE (proxy + WAF + SSL)                     │
│                                                                                │
│  webshooks.com  *.webshooks.com  argfy.com  luzguffantti.com  anamurat.com    │
│        │               │               │            │               │         │
└────────┼───────────────┼───────────────┼────────────┼───────────────┼─────────┘
         │               │               │            │               │
         ▼               ▼               ▼            ▼               ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                         HETZNER CX43 (4 vCPU · 16GB · 160GB NVMe)             │
│                                                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │                          TRAEFIK (reverse proxy)                        │   │
│  │  Dominios → Routers por label → Container correcto                     │   │
│  │  SSL automático via Let's Encrypt                                      │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │                          DOCKER ECOSYSTEM                               │   │
│  │                                                                          │   │
│  │  ┌───────────────────┐  ┌───────────────────┐  ┌────────────────────┐  │   │
│  │  │   pg-core          │  │   pg-demos         │  │   redis-shared     │  │   │
│  │  │   (Postgres 16)    │  │   (Postgres 16)    │  │   (Redis 7)        │  │   │
│  │  │                     │  │                     │  │                    │  │   │
│  │  │  webshooks_db      │  │  tienda_db          │  │  App cache         │  │   │
│  │  │  argfy_db          │  │  electronica_db     │  │  Session store     │  │   │
│  │  │  luzguffantti_db   │  │  zapateria_db       │  │  RQ queue (future) │  │   │
│  │  │  anamurat_db       │  │  clinica_db         │  │                    │  │   │
│  │  │                     │  │  instructor_db      │  │                    │  │   │
│  │  │  (schemas × tenant)│  │  yoga_db            │  │                    │  │   │
│  │  │                     │  │  entrenador_db      │  │                    │  │   │
│  │  └───────────────────┘  └───────────────────┘  └────────────────────┘  │   │
│  │                                                                          │   │
│  │  ┌──────────────────────────────────────────────────────────────────┐   │   │
│  │  │                    CONTENEDORES POR PROYECTO                      │   │   │
│  │  │                                                                  │   │   │
│  │  │  webshooks/          argfy/              demos/ (×7)             │   │   │
│  │  │  ├─ ws-api           ├─ argfy-api        ├─ tienda-api           │   │   │
│  │  │  ├─ ws-web           ├─ argfy-web        ├─ tienda-web           │   │   │
│  │  │  ├─ ws-scheduler     ├─ argfy-scheduler  ├─ electronica-api      │   │   │
│  │  │  └─ ws-worker        └─ argfy-worker     └─ electronica-web      │   │   │
│  │  │                                           └─ ...                  │   │   │
│  │  │                                                                  │   │   │
│  │  │  luzguffantti/       anamurat/                                   │   │   │
│  │  │  └─ luzguf-web       └─ anamurat-web                             │   │   │
│  │  └──────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                          │   │
│  │  ┌─────────────────── OBSERVABILITY ─────────────────────────────────┐  │   │
│  │  │  prometheus │ grafana (mon.webshooks.com) │ loki │ promtail      │  │   │
│  │  │  node-exporter │ cadvisor                                        │  │   │
│  │  └──────────────────────────────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │                              VOLUMES                                    │   │
│  │  pg_core_data  pg_demos_data  redis_data  letsencrypt  grafana_data    │   │
│  │  prometheus_data  loki_data  traefik_logs                               │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │                              BACKUPS                                    │   │
│  │  /backups/pg_core/    (pg_dumpall diario, retención 14d)               │   │
│  │  /backups/pg_demos/   (pg_dumpall diario, retención 14d)               │   │
│  │  /backups/config/     (.env + compose cifrados GPG, retención 30d)     │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Naming Conventions

### 3.1. Contenedores Docker

```
Regla: {proyecto}-{rol}[-{variante}]

webshooks-api              # FastAPI backend
webshooks-web              # Next.js frontend
webshooks-scheduler        # APScheduler
webshooks-worker           # ETL (futuro)
argfy-api
argfy-web
argfy-scheduler
argfy-worker
luzguffantti-web           # Portfolio (solo frontend)
anamurat-web               # Portfolio (solo frontend)
tienda-api
tienda-web
electronica-api
electronica-web
zapateria-api
zapateria-web
clinica-api
clinica-web
instructor-api
instructor-web
yoga-api
yoga-web
entrenador-api
entrenador-web
pg-core                    # Postgres compartido (webshooks + argfy + projects)
pg-demos                   # Postgres compartido (demos)
redis-shared               # Redis compartido
pgbouncer-core             # Pool para pg-core
pgbouncer-demos            # Pool para pg-demos
traefik                    # Reverse proxy
```

### 3.2. Imágenes Docker

```
Regla: ghcr.io/{org}/{proyecto}-{rol}:{tag}

ghcr.io/webshooks/webshooks-api:latest
ghcr.io/webshooks/webshooks-web:latest
ghcr.io/argfy/argfy-api:v1.2.3
ghcr.io/luzguffantti/luzguffantti-web:git-abc123
ghcr.io/tienda/tienda-api:latest

Tags:
  latest          → último build verde de main
  v{major}.{minor}.{patch}  → releases semánticos
  git-{sha}       → builds específicos (rollback)
```

### 3.3. Bases de Datos

```
Instancia      Database                Esquemas (multi-tenant)
──────────     ────────────             ─────────────────────────
pg-core        webshooks_db             {tenant_id} por schema
pg-core        argfy_db                 {tenant_id} por schema
pg-core        luzguffantti_db          public
pg-core        anamurat_db              public
pg-demos       tienda_db                public
pg-demos       electronica_db           public
pg-demos       zapateria_db             public
pg-demos       clinica_db               public
pg-demos       instructor_db            public
pg-demos       yoga_db                  public
pg-demos       entrenador_db            public
```

### 3.4. Volúmenes Docker

```
pg_core_data          # /var/lib/postgresql/data (pg-core)
pg_demos_data         # /var/lib/postgresql/data (pg-demos)
redis_data            # /data (Redis)
pgbouncer_core_logs   # /var/log/pgbouncer
grafana_data          # /var/lib/grafana
prometheus_data       # /prometheus
loki_data             # /loki
traefik_letsencrypt   # /letsencrypt (certificados)
traefik_logs          # /var/log/traefik
```

### 3.5. Redes Docker

```
Nombre                    Propósito
─────                     ─────────
infrastructure_frontend   Traefik ↔ web containers (todos los proyectos)
infrastructure_backend    API ↔ servicios internos (PgBouncer, Redis)
infrastructure_db_core    pg-core ↔ PgBouncer
infrastructure_db_demos   pg-demos ↔ APIs de demos
infrastructure_cache      Redis ↔ apps que lo usan
infrastructure_observability  Prometheus / Grafana / Loki
# infrastructure_public     Eliminada — Traefik usa host ports (80:80, 443:443), no necesita red externa
```

### 3.6. Variables de Entorno

```
Regla: {PROYECTO}_{PROPIEDAD}

webshooks:
  WS_DOMAIN=webshooks.com
  WS_API_DOMAIN=api.webshooks.com
  WS_DB_HOST=pgbouncer-core
  WS_DB_PORT=6432
  WS_DB_NAME=webshooks_db
  WS_DB_USER=webshooks
  WS_DB_PASS=***

argfy:
  ARGFY_DOMAIN=argfy.com
  ARGFY_API_DOMAIN=api.argfy.com
  ARGFY_DB_HOST=pgbouncer-core
  ARGFY_DB_PORT=6432
  ARGFY_DB_NAME=argfy_db
  ARGFY_DB_USER=argfy
  ARGFY_DB_PASS=***

tienda (demo):
  TIENDA_DOMAIN=tienda.webshooks.com
  TIENDA_DB_HOST=pg-demos
  TIENDA_DB_PORT=5432
  TIENDA_DB_NAME=tienda_db

shared:
  REDIS_HOST=redis-shared
  REDIS_PORT=6379
  SENTRY_DSN=https://xxx@sentry.io/xxx
```

---

## 4. Estructura de Carpetas en VPS

```
/
├── projects/                              # Código + config de cada proyecto
│   ├── webshooks/                         # webshooks.com (control plane)
│   │   ├── docker-compose.yml
│   │   ├── .env
│   │   └── postgres/
│   │       └── init/
│   │           └── 01-schemas.sql
│   │
│   ├── argfy/                             # argfy.com
│   │   ├── docker-compose.yml
│   │   ├── .env
│   │   └── postgres/
│   │       └── init/
│   │
│   ├── luzguffantti/                      # luzguffantti.com
│   │   ├── docker-compose.yml
│   │   └── .env
│   │
│   ├── anamurat/                          # anamurat.com
│   │   ├── docker-compose.yml
│   │   └── .env
│   │
│   └── demos/
│       ├── tienda/
│       │   ├── docker-compose.yml
│       │   └── .env
│       ├── electronica/
│       │   ├── docker-compose.yml
│       │   └── .env
│       ├── zapateria/
│       ├── clinica/
│       ├── instructor/
│       ├── yoga/
│       └── entrenador/
│
├── infrastructure/                        # Stack compartido entre proyectos
│   ├── docker-compose.yml                 # Traefik + Postgres + Redis + Obs
│   ├── .env
│   ├── traefik/
│   │   └── traefik.yml
│   ├── postgres/
│   │   └── core-init/
│   │       └── 00-create-dbs.sql
│   ├── prometheus/
│   │   └── prometheus.yml
│   ├── grafana/
│   │   ├── dashboards/
│   │   └── datasources/
│   ├── loki/
│   │   └── loki.yml
│   └── promtail/
│       └── promtail.yml
│
├── backups/
│   ├── scripts/
│   │   └── backup.sh
│   ├── pg_core/                           # pg_dumpall de pg-core
│   ├── pg_demos/                          # pg_dumpall de pg-demos
│   └── config/                            # .env cifrados (GPG)
│
├── logs/
│   ├── traefik/
│   └── projects/                          # fallback si Loki no está
│
└── scripts/
    ├── healthcheck.sh                     # VPS health check
    ├── deploy.sh                          # Deploy helper
    └── rotate-logs.sh                     # Rotación de logs locales
```

---

## 5. Organización de Repositorios

```
github.com/webshooks/
├── webshooks                    → webshooks.com (control plane)
├── demo-tienda                  → tienda.webshooks.com
├── demo-electronica             → electronica.webshooks.com
├── demo-zapateria               → zapateria.webshooks.com
├── demo-clinica                 → clinica.webshooks.com
├── demo-instructor              → instructor.webshooks.com
├── demo-yoga                    → yoga.webshooks.com
├── demo-personal-trainer        → entrenador.webshooks.com
└── infrastructure               → Traefik, observabilidad, scripts compartidos

github.com/argfy/
└── argfy                        → argfy.com

github.com/luzguffantti/
└── luzguffantti                 → luzguffantti.com

github.com/anamurat/
└── anamurat                     → anamurat.com
```

### ⚠️ Monorepo para demos (alternativa recomendada si comparten stack)

Si las demos (tienda, electronica, yoga, etc.) comparten stack, componentes y arquitectura, considerar **monorepo** en vez de repo por demo:

```
github.com/webshooks/webshooks-demos/
├── apps/
│   ├── tienda/
│   │   ├── backend/
│   │   ├── frontend/
│   │   └── Dockerfile
│   ├── yoga/
│   ├── clinica/
│   └── electronica/
├── packages/
│   ├── ui/            # Componentes compartidos
│   ├── api-client/    # Cliente API compartido
│   └── config/        # ESLint, TS config, etc.
├── .github/workflows/
│   └── deploy.yml     # Matrix build por app
└── docker-compose.yml # Multi-app compose
```

**Ventajas:** CI/CD compartido, dependencias compartidas, un solo `npm install`, cambios cross-app en un solo PR.
**Regla:** Si 3+ demos usan el mismo stack → monorepo. Si cada demo es completamente distinto → repo por proyecto.

### Estructura interna de cada repo de proyecto:

```
{proyecto}/
├── backend/                     # FastAPI / Node / Go / etc
│   ├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── ...
├── frontend/                    # Next.js / React / etc
│   ├── src/
│   ├── Dockerfile
│   ├── package.json
│   └── ...
├── .github/
│   └── workflows/
│       └── deploy.yml           # CI/CD: test → build → push → deploy
├── docker-compose.yml           # Stack local del proyecto
├── .env.example
├── README.md
└── Makefile                     # make dev / make build / make deploy
```

---

## 6. Organización Coolify

```
Coolify
├── Projects
│   ├── webshooks (control plane)
│   │   ├── webshooks-api
│   │   ├── webshooks-web
│   │   ├── webshooks-scheduler
│   │   └── webshooks-worker (future)
│   │
│   ├── argfy
│   │   ├── argfy-api
│   │   ├── argfy-web
│   │   ├── argfy-scheduler
│   │   └── argfy-worker
│   │
│   ├── luzguffantti
│   │   └── luzguffantti-web
│   │
│   ├── anamurat
│   │   └── anamurat-web
│   │
│   ├── demos
│   │   ├── tienda-web / tienda-api
│   │   ├── electronica-web / electronica-api
│   │   ├── zapateria-web / zapateria-api
│   │   ├── clinica-web / clinica-api
│   │   ├── instructor-web / instructor-api
│   │   ├── yoga-web / yoga-api
│   │   └── entrenador-web / entrenador-api
│   │
│   ├── shared-services          ← Se despliega UNA vez
│   │   ├── pg-core              (Postgres 16)
│   │   ├── pg-demos             (Postgres 16)
│   │   ├── redis-shared         (Redis 7)
│   │   ├── pgbouncer-core       (Pool pg-core)
│   │   └── pgbouncer-demos      (Pool pg-demos)
│   │
│   └── observability         ← Traefik: usa el built-in de Coolify
│       ├── grafana
│       ├── prometheus
│       ├── loki
│       ├── promtail
│       ├── node-exporter
│       └── cadvisor
│
└── Servers
    └── hetzner-cx43
        ├── Labels: region=hel1, env=prod, provider=hetzner
        └── Proxy: Traefik (built-in Coolify)
```

### Reglas Coolify:

| Regla | Valor |
|-------|-------|
| **Proxy** | Traefik (Coolify lo gestiona automáticamente) |
| **Build** | Coolify builda desde Dockerfile en cada push |
| **Deploy** | Webhook GitHub → Coolify, rolling update |
| **Env vars** | En Coolify UI por servicio (nunca en .env en repo) |
| **Secrets** | Toggle "encrypted" en Coolify para DB_PASS, SECRET_KEY, etc. |
| **Healthcheck** | Definido en Dockerfile/Compose (Coolify lo usa para rolling) |
| **Replicas** | `web=1, api=1-2, scheduler=1, worker=1` |
| **Domains** | Coolify asigna dominio automáticamente via Traefik |

---

## 7. Dominios y Subdominios

```
webshooks.com                     # Control plane (frontend)
www.webshooks.com                 # Redirect a webshooks.com
api.webshooks.com                 # Control plane (backend API)
mon.webshooks.com                 # Grafana (auth básico + IP restrict)

tienda.webshooks.com              # Demo ecommerce
electronica.webshooks.com         # Demo electronica
zapateria.webshooks.com           # Demo zapateria
clinica.webshooks.com             # Demo clinica
instructor.webshooks.com          # Demo instructor
yoga.webshooks.com                # Demo yoga
entrenador.webshooks.com          # Demo personal trainer

argfy.com                         # Plataforma financiera (frontend)
www.argfy.com                     # Redirect a argfy.com
api.argfy.com                     # API financiera

luzguffantti.com                  # Portfolio freelance
www.luzguffantti.com              # Redirect
anamurat.com                      # Portfolio freelance
www.anamurat.com                  # Redirect
```

### Cloudflare DNS:

```
Registro                  Tipo    Proxy     Destino
─────────                 ────    ─────     ──────
argfy.com                 A       Proxied   {VPS_IP}
www.argfy.com             CNAME   Proxied   argfy.com
api.argfy.com             A       Proxied   {VPS_IP}
webshooks.com             A       Proxied   {VPS_IP}
www.webshooks.com         CNAME   Proxied   webshooks.com
api.webshooks.com         A       Proxied   {VPS_IP}
mon.webshooks.com         A       Proxied   {VPS_IP}
*.webshooks.com           CNAME   Proxied   webshooks.com   ← wildcard para demos
luzguffantti.com          A       Proxied   {VPS_IP}
anamurat.com              A       Proxied   {VPS_IP}
```

### Cloudflare Settings:

| Setting | Valor |
|---------|-------|
| SSL/TLS | Full (strict) |
| Always Use HTTPS | ON |
| HSTS | ON (max-age=31536000, includeSubdomains, preload) |
| WAF | ON (Managed Rules) |
| Bot Fight Mode | ON |
| Rate Limiting | 100 req/10s por IP |
| Minimum TLS Version | 1.3 |
| Orange cloud | ON para todos los dominios |

---

## 8. Mapa de Puertos

```
Servicio            Container   Host        Red             Notas
───────             ─────────   ────        ───             ─────
traefik (web)       80          80          public          HTTP → HTTPS redirect
traefik (websecure) 443         443         public          TLS / SSL
traefik (admin)     8080        ─           ─               Solo internal
ssh                 ─           22          host            Key-only + fail2ban
coolify             3000        8000        host            Lock a IPs admin

pg-core             5432        ─           db_core         Sin puerto host
pg-demos            5433        ─           db_demos        Sin puerto host
pgbouncer-core      6432        ─           backend,db_core Pool para pg-core
pgbouncer-demos     6433        ─           backend,db_demos Pool para pg-demos
redis-shared        6379        ─           cache           Sin puerto host

grafana             3000        ─           observability   Via Traefik (mon.*)
prometheus          9090        ─           observability   Solo internal
loki                3100        ─           observability   Solo internal
node-exporter       9100        ─           observability   Solo internal
cadvisor            8080        ─           observability   Solo internal

*web                3000        ─           frontend        Via Traefik
*api                8000        ─           backend         Via Traefik
*scheduler          ─           ─           backend         Sin HTTP
*worker             ─           ─           backend         Sin HTTP
```

**Regla de oro:** ningún container expone puertos al host excepto Traefik (80/443) y Coolify (8000). DBs, Redis, PgBouncer, y servicios de observabilidad solo accesibles via redes Docker internas.

---

## 9. Redes Docker

```
# infrastructure_public — eliminada. Traefik usa host ports (80:80, 443:443).
# No necesita red externa de Docker. Host ports bypass Docker networks.

infrastructure_frontend
  ├── traefik              ← Proxy inverso
  ├── *-web (todos)        ← Next.js, React, etc.

infrastructure_backend
  ├── *-api (todos)        ← FastAPI, Node, etc.
  ├── *-scheduler          ← APScheduler
  ├── *-worker             ← ETL
  ├── pgbouncer-core       ← Pool conexiones pg-core
  ├── pgbouncer-demos      ← Pool conexiones pg-demos
  └── redis-shared         ← Cache

infrastructure_db_core (internal: true)
  ├── pg-core              ← Postgres (webshooks + argfy + projects)
  └── pgbouncer-core       ← Solo PgBouncer habla con Postgres

infrastructure_db_demos (internal: true)
  ├── pg-demos             ← Postgres (demos)
  └── pgbouncer-demos      ← Solo PgBouncer habla con Postgres

infrastructure_cache (internal: true)
  └── redis-shared         ← Redis (solo accesible por backend)

infrastructure_observability
  ├── prometheus
  ├── grafana
  ├── loki
  ├── promtail
  ├── node-exporter
  └── cadvisor
```

### Flujo de conexión DB:

```
web (frontend)
  └── HTTP → Traefik → api (backend)
                          └── TCP:6432 → pgbouncer-core
                                            └── TCP:5432 → pg-core (red db_core)
```

**Seguridad en capas:**
- `frontend` no ve `backend`
- `backend` no ve `db_core` directamente, solo via PgBouncer
- `db_core` es `internal: true` — ni siquiera Traefik puede llegar
- `db_demos` es `internal: true`
- `cache` es `internal: true`

---

## 10. Estrategia Postgres

### Dos instancias, justificación:

| Aspecto | pg-core | pg-demos |
|---------|---------|----------|
| Contiene | webshooks, argfy, projects | tienda, electronica, etc. |
| Prioridad | Crítica | Standard |
| Backup | pg_dumpall diario | pg_dumpall diario |
| Escala futura | Se queda en VPS1 | Se mueve a VPS2 si crece |
| RAM estimada | 1GB | 1GB |

### ¿Por qué no 1 sola instancia?

- Una consulta pesada de un demo (ej: reporte masivo) no afecta webshooks
- Backup independiente: restaurar un demo no requiere restaurar webshooks
- Si los demos crecen, migrar pg-demos a otra VPS es mover 1 container

### ¿Por qué no 10 instancias (una por demo)?

- Cada Postgres consume ~500MB-1GB RAM base
- En 16GB RAM, 2 Postgres + apps = factible
- 10 Postgres = 5-10GB solo en DBs = inviable

### PgBouncer

```
pgbouncer-core (pool transaccional):
  └── Max client conn: 100
  └── Default pool size: 25
  └── Sirve a: webshooks-api, argfy-api, luzguffantti-api, anamurat-api

pgbouncer-demos (pool transaccional):
  └── Max client conn: 50
  └── Default pool size: 10
  └── Sirve a: tienda-api, electronica-api, etc.
```

---

## 11. Estrategia Redis

### Una instancia compartida:

```yaml
redis:
  image: redis:7-alpine
  container_name: redis-shared
  command: >
    redis-server
    --requirepass ${REDIS_PASSWORD}
    --save 300 1
    --maxmemory 512mb
    --maxmemory-policy allkeys-lru
```

### Prefijos de keys por proyecto:

```
webshooks:session:{token}
webshooks:cache:{key}
argfy:session:{token}
argfy:cache:{key}
tienda:cache:{key}
```

### Uso por proyecto:

| Servicio | Redis usa para |
|----------|---------------|
| webshooks-api | Sesiones, rate limit, cache |
| argfy-api | Sesiones, rate limit, cache, cola RQ (future) |
| demos-api | Cache (sesiones cada uno en su DB) |

---

## 12. Infraestructura Base — docker-compose

Este archivo vive en `/infrastructure/docker-compose.yml` y contiene todo el stack compartido. Se despliega UNA vez y los proyectos lo referencian via `external: true` networks y volumes.

> **⚠️ Traefik:** NO se incluye aquí. Coolify provee Traefik built-in que auto-descubre containers por labels. Si usás Coolify (recomendado), los routers se definen via labels en cada proyecto, no acá. Si no usás Coolify, agregá Traefik manualmente a este compose.

```yaml
# /infrastructure/docker-compose.yml
# Traefik: NO se incluye — Coolify provee Traefik built-in.
# Los routers se definen via labels Traefik en cada proyecto.

services:
  # ── Postgres Core ──────────────────────────────────────
  pg-core:
    image: postgres:16-alpine
    container_name: pg-core
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: ${PG_CORE_PASS}
    volumes:
      - "pg_core_data:/var/lib/postgresql/data"
      - "./postgres/core-init:/docker-entrypoint-initdb.d:ro"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    mem_limit: 1g
    networks:
      - infrastructure_db_core

  # ── Postgres Demos ─────────────────────────────────────
  pg-demos:
    image: postgres:16-alpine
    container_name: pg-demos
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: ${PG_DEMOS_PASS}
    volumes:
      - "pg_demos_data:/var/lib/postgresql/data"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    mem_limit: 1g
    networks:
      - infrastructure_db_demos

  # ── PgBouncer Core ─────────────────────────────────────
  pgbouncer-core:
    image: edoburu/pgbouncer:latest
    container_name: pgbouncer-core
    restart: unless-stopped
    environment:
      DATABASE_URL: postgres://postgres:${PG_CORE_PASS}@pg-core:5432/postgres
      POOL_MODE: transaction
      MAX_CLIENT_CONN: 100
      DEFAULT_POOL_SIZE: 25
    depends_on:
      pg-core:
        condition: service_healthy
    networks:
      - infrastructure_backend
      - infrastructure_db_core

  # ── PgBouncer Demos ────────────────────────────────────
  pgbouncer-demos:
    image: edoburu/pgbouncer:latest
    container_name: pgbouncer-demos
    restart: unless-stopped
    environment:
      DATABASE_URL: postgres://postgres:${PG_DEMOS_PASS}@pg-demos:5432/postgres
      POOL_MODE: transaction
      MAX_CLIENT_CONN: 50
      DEFAULT_POOL_SIZE: 10
    depends_on:
      pg-demos:
        condition: service_healthy
    networks:
      - infrastructure_backend
      - infrastructure_db_demos

  # ── Redis ──────────────────────────────────────────────
  redis-shared:
    image: redis:7-alpine
    container_name: redis-shared
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD} --save 300 1 --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - "redis_data:/data"
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    mem_limit: 512m
    networks:
      - infrastructure_cache

  # ── Prometheus ─────────────────────────────────────────
  prometheus:
    image: prom/prometheus:v2.53
    container_name: prometheus
    restart: unless-stopped
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
      - "--storage.tsdb.retention.time=15d"
    volumes:
      - "./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro"
      - "prometheus_data:/prometheus"
    mem_limit: 256m
    networks:
      - infrastructure_observability

  # ── Grafana ────────────────────────────────────────────
  grafana:
    image: grafana/grafana:11.1
    container_name: grafana
    restart: unless-stopped
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD}
      GF_AUTH_ANONYMOUS_ENABLED: "false"
      GF_SERVER_ROOT_URL: https://mon.webshooks.com
    volumes:
      - "grafana_data:/var/lib/grafana"
      - "./grafana/dashboards:/etc/grafana/provisioning/dashboards:ro"
      - "./grafana/datasources:/etc/grafana/provisioning/datasources:ro"
    depends_on:
      - prometheus
    mem_limit: 256m
    networks:
      - infrastructure_observability
      - infrastructure_frontend
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.grafana.rule=Host(`mon.webshooks.com`)"
      - "traefik.http.routers.grafana.tls.certresolver=letsencrypt"
      - "traefik.http.services.grafana.loadbalancer.server.port=3000"
      - "traefik.http.routers.grafana.middlewares=auth-basic"

  # ── Node Exporter ──────────────────────────────────────
  node-exporter:
    image: prom/node-exporter:v1.8
    container_name: node-exporter
    restart: unless-stopped
    command:
      - "--path.rootfs=/host"
    volumes:
      - "/:/host:ro,rslave"
    pid: host
    mem_limit: 64m
    networks:
      - infrastructure_observability

  # ── Blackbox Exporter ──────────────────────────────────
  blackbox-exporter:
    image: prom/blackbox-exporter:v0.25
    container_name: blackbox-exporter
    restart: unless-stopped
    command:
      - "--config.file=/config/blackbox.yml"
    volumes:
      - "./prometheus/blackbox.yml:/config/blackbox.yml:ro"
    mem_limit: 32m
    networks:
      - infrastructure_observability

# ── Loki + Promtail + cAdvisor (FASE 2) ─────────────────
# Se agregan cuando haya suficiente RAM o necesidad real.
# Por ahora: Sentry para errores, Docker logs + journalctl para debugging.
# Descomentar cuando estés listo:
#
#  loki:
#    image: grafana/loki:3.1
#    container_name: loki
#    restart: unless-stopped
#    command: -config.file=/etc/loki/loki.yml
#    volumes:
#      - "./loki/loki.yml:/etc/loki/loki.yml:ro"
#      - "loki_data:/loki"
#    mem_limit: 256m
#    networks:
#      - infrastructure_observability
#
#  promtail:
#    image: grafana/promtail:3.1
#    container_name: promtail
#    restart: unless-stopped
#    command: -config.file=/etc/promtail/promtail.yml
#    volumes:
#      - "./promtail/promtail.yml:/etc/promtail/promtail.yml:ro"
#      - "/var/log:/var/log:ro"
#      - "/var/lib/docker/containers:/var/lib/docker/containers:ro"
#    mem_limit: 128m
#    networks:
#      - infrastructure_observability
#
#  cadvisor:
#    image: gcr.io/cadvisor/cadvisor:v0.49
#    container_name: cadvisor
#    restart: unless-stopped
#    volumes:
#      - "/:/rootfs:ro"
#      - "/var/run:/var/run:ro"
#      - "/sys:/sys:ro"
#      - "/var/lib/docker/:/var/lib/docker:ro"
#      - "/dev/disk/:/dev/disk:ro"
#    privileged: true
#    mem_limit: 128m
#    networks:
#      - infrastructure_observability

  # ── Uptime Kuma ────────────────────────────────────────
  uptime-kuma:
    image: louislam/uptime-kuma:1
    container_name: uptime-kuma
    restart: unless-stopped
    volumes:
      - "uptime_kuma_data:/app/data"
    # No ports — solo via Traefik
    mem_limit: 128m
    networks:
      - infrastructure_frontend
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.uptime-kuma.rule=Host(`status.webshooks.com`)"
      - "traefik.http.routers.uptime-kuma.tls.certresolver=letsencrypt"
      - "traefik.http.services.uptime-kuma.loadbalancer.server.port=3001"

# ── CrowdSec (FASE 2 — SEGURIDAD) ──────────────────────
# Descomentar cuando Cloudflare WAF no sea suficiente.
# Cloudflare ya cubre: DDoS, bots, rate limiting, WAF.
# CrowdSec agrega: detección local, bouncer Traefik, blocking IPs.
#
#  crowdsec:
#    image: crowdsecurity/crowdsec:v1.6
#    container_name: crowdsec
#    restart: unless-stopped
#    environment:
#      COLLECTIONS: "crowdsecurity/traefik crowdsecurity/linux crowdsecurity/http-cve"
#      GID: "${PGID:-1000}"
#      UID: "${PUID:-1000}"
#    volumes:
#      - "crowdsec_data:/var/lib/crowdsec/data"
#      - "crowdsec_config:/etc/crowdsec"
#      - "/var/log:/var/log:ro"
#    mem_limit: 128m
#    networks:
#      - infrastructure_observability
#    cap_add:
#      - NET_ADMIN
#      - SYS_ADMIN

volumes:
  pg_core_data:
    name: pg_core_data
  pg_demos_data:
    name: pg_demos_data
  redis_data:
    name: redis_data
  prometheus_data:
    name: prometheus_data
  grafana_data:
    name: grafana_data
  uptime_kuma_data:
    name: uptime_kuma_data
  crowdsec_data:
    name: crowdsec_data
  crowdsec_config:
    name: crowdsec_config

networks:
  infrastructure_frontend:
    name: infrastructure_frontend
    driver: bridge
  infrastructure_backend:
    name: infrastructure_backend
    driver: bridge
  infrastructure_db_core:
    name: infrastructure_db_core
    driver: bridge
    internal: true
  infrastructure_db_demos:
    name: infrastructure_db_demos
    driver: bridge
    internal: true
  infrastructure_cache:
    name: infrastructure_cache
    driver: bridge
    internal: true
  infrastructure_observability:
    name: infrastructure_observability
    driver: bridge
```

---

## 13. Template de Proyecto — docker-compose

Cada proyecto define su propio `docker-compose.yml` que referencia las networks externas de la infraestructura base.

```yaml
# /projects/demos/tienda/docker-compose.yml
services:
  api:
    image: ghcr.io/webshooks/tienda-api:${TAG:-latest}
    container_name: tienda-api
    restart: unless-stopped
    environment:
      DOMAIN: tienda.webshooks.com
      DATABASE_URL: postgresql://postgres:${PG_DEMOS_PASS}@pgbouncer-demos:6433/tienda_db
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis-shared:6379/0
      REDIS_PREFIX: tienda:
      SECRET_KEY: ${TIENDA_SECRET_KEY}
      SENTRY_DSN: ${SENTRY_DSN}
      LOG_LEVEL: info
    depends_on:
      api-migrate:
        condition: service_completed_successfully
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 15s
    mem_limit: 256m
    cpus: 0.5
    networks:
      - infrastructure_backend
      - infrastructure_frontend
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.tienda-api.rule=Host(`tienda.webshooks.com`) && PathPrefix(`/api`)"
      - "traefik.http.routers.tienda-api.tls.certresolver=letsencrypt"
      - "traefik.http.services.tienda-api.loadbalancer.server.port=8000"

  web:
    image: ghcr.io/webshooks/tienda-web:${TAG:-latest}
    container_name: tienda-web
    restart: unless-stopped
    environment:
      NEXT_PUBLIC_API_BASE: https://tienda.webshooks.com/api
    depends_on:
      api:
        condition: service_started
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3000/"]
      interval: 30s
      timeout: 5s
      retries: 3
    mem_limit: 256m
    cpus: 0.5
    networks:
      - infrastructure_frontend
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.tienda-web.rule=Host(`tienda.webshooks.com`)"
      - "traefik.http.routers.tienda-web.tls.certresolver=letsencrypt"
      - "traefik.http.services.tienda-web.loadbalancer.server.port=3000"

  api-migrate:
    image: ghcr.io/webshooks/tienda-api:${TAG:-latest}
    container_name: tienda-migrate
    restart: no
    command: ["python", "-m", "app.migrate"]
    environment:
      DATABASE_URL: postgresql://postgres:${PG_DEMOS_PASS}@pgbouncer-demos:6433/tienda_db
    networks:
      - infrastructure_backend

networks:
  infrastructure_frontend:
    external: true
    name: infrastructure_frontend
  infrastructure_backend:
    external: true
    name: infrastructure_backend
```

---

## 14. webshooks.com — Control Plane

webshooks.com es el **panel de control** del ecosistema. **No** es un API gateway ni un proxy reverso. Cada demo/project funciona de forma 100% independiente en su subdominio.

### Funcionalidades:

```
webshooks.com dashboard:
├── Lista de proyectos registrados
├── Estado de cada demo (up/down/error via healthcheck)
├── Configuración de webhooks entrantes por proyecto
├── Logs centralizados (vía Loki API)
├── API keys por proyecto
└── Métricas de uso (requests, errores, latencia)

Multi-tenancy:
└── webshooks_db usa schemas de PostgreSQL
└── Cada proyecto registrado = un schema {tenant_id}
└── Aislamiento a nivel DB sin multiplicar instancias
```

### Conexión a DB:

```
webshooks-api → pgbouncer-core:6432 → webshooks_db → schema={tenant_id}
```

### Rutas Traefik para webshooks:

```yaml
# Router labels en webshooks docker-compose
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.ws-web.rule=Host(`webshooks.com`) || Host(`www.webshooks.com`)"
  - "traefik.http.routers.ws-web.tls.certresolver=letsencrypt"
  - "traefik.http.services.ws-web.loadbalancer.server.port=3000"

  - "traefik.http.routers.ws-api.rule=Host(`api.webshooks.com`)"
  - "traefik.http.routers.ws-api.tls.certresolver=letsencrypt"
  - "traefik.http.services.ws-api.loadbalancer.server.port=8000"
```

---

## 15. Estrategia de Backups

```bash
#!/bin/bash
# /backups/scripts/backup.sh
set -euo pipefail

TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups
RETENTION_DB=14
RETENTION_CONFIG=30
GPG_RECIPIENT=ops@webshooks.com

log() { echo "[$TIMESTAMP] $*"; }

# ── 1. pg-core (webshooks + argfy + projects) ───────────
log "Backing up pg-core..."
docker exec pg-core pg_dumpall -U postgres | gzip > "$BACKUP_DIR/pg_core/pg_core_$TIMESTAMP.sql.gz"
log "pg-core: $(du -h "$BACKUP_DIR/pg_core/pg_core_$TIMESTAMP.sql.gz" | cut -f1)"

# ── 2. pg-demos (tienda, electronica, etc.) ────────────
log "Backing up pg-demos..."
docker exec pg-demos pg_dumpall -U postgres | gzip > "$BACKUP_DIR/pg_demos/pg_demos_$TIMESTAMP.sql.gz"
log "pg-demos: $(du -h "$BACKUP_DIR/pg_demos/pg_demos_$TIMESTAMP.sql.gz" | cut -f1)"

# ── 3. Config (docker-compose + .env cifrados) ─────────
log "Backing up config..."
tar czf /tmp/config_$TIMESTAMP.tar.gz \
  -C / projects/ \
  -C / infrastructure/
gpg --encrypt --recipient "$GPG_RECIPIENT" \
  --output "$BACKUP_DIR/config/config_$TIMESTAMP.tar.gz.gpg" \
  /tmp/config_$TIMESTAMP.tar.gz
rm -f /tmp/config_$TIMESTAMP.tar.gz
log "Config encrypted backup created"

# ── 4. Retention ────────────────────────────────────────
find "$BACKUP_DIR/pg_core"  -name "*.sql.gz" -mtime +$RETENTION_DB -delete
find "$BACKUP_DIR/pg_demos" -name "*.sql.gz" -mtime +$RETENTION_DB -delete
find "$BACKUP_DIR/config"   -name "*.tar.gz.gpg" -mtime +$RETENTION_CONFIG -delete
log "Retention cleanup done"
```

### Disaster Recovery — RPO / RTO:

| Métrica | Objetivo | Cómo se logra |
|---------|----------|---------------|
| **RPO** | ≤ 6 horas | Backup pg_dumpall cada 6h + WAL archiving (future) |
| **RTO** | ≤ 2 horas | docker-compose up + pg_restore desde offsite |
| **RPO crítico** (webshooks) | ≤ 1 hora | WAL archiving a R2 (future: pg_receivewal continuo) |
| **RTO crítico** (webshooks) | ≤ 30 min | Script de restore automatizado + VPS snapshot |

**Restore procedure documentado (probar mensualmente):**

```bash
# 1. Provisionar nuevo VPS (o reparar actual)
# 2. Instalar Docker + Docker Compose
# 3. Descargar backups offsite:
rclone copy :s3:argfy-backups/pg_core/pg_core_latest.sql.gz /backups/pg_core/
rclone copy :s3:argfy-backups/config/config_latest.tar.gz.gpg /backups/config/
# 4. Restaurar config:
gpg --decrypt /backups/config/config_latest.tar.gz.gpg | tar xz -C /
# 5. Levantar infraestructura:
docker compose -f /infrastructure/docker-compose.yml up -d
# 6. Restaurar DB:
gunzip -c /backups/pg_core/pg_core_latest.sql.gz | docker exec -i pg-core psql -U postgres
# 7. Levantar proyectos:
docker compose -f /projects/webshooks/docker-compose.yml up -d
# 8. Verificar healthchecks
```

**Riesgo actual:** RTO > 2h porque el restore no está automatizado en un solo script.
**Mitigación:** crear `/scripts/full-restore.sh` que haga 1-8 automáticamente.

### Offsite Backups (obligatorio):

Los backups locales en la misma VPS **no son suficientes**. Si la VPS muere, pierde todo.

```bash
# /backups/scripts/backup-offsite.sh
# Se ejecuta DESPUÉS del backup local. Sube a Cloudflare R2 / Backblaze B2 / S3.
# $5/mes en R2 o B2.

rclone copy /backups/pg_core/pg_core_latest.sql.gz \
  :s3:argfy-backups/pg_core/  --provider=Cloudflare

rclone copy /backups/pg_demos/pg_demos_latest.sql.gz \
  :s3:argfy-backups/pg_demos/ --provider=Cloudflare

rclone copy /backups/config/config_latest.tar.gz.gpg \
  :s3:argfy-backups/config/   --provider=Cloudflare
```

**Mínimo obligatorio:** backup diario a Cloudflare R2 (~$0.36/GB/mes) o Backblaze B2 (~$0.006/GB/mes).
**Snapshots del VPS:** Hetzner permite snapshots automáticos semanales (adicional).

### Cron:

```cron
0 */6 * * * /backups/scripts/backup.sh                 # Cada 6h DB + Config
30 */6 * * * /backups/scripts/backup-offsite.sh         # 30min después, subir a R2
0 4 1 * * /backups/scripts/test-restore.sh              # 1er día del mes: test restore
```

### Restore:

```bash
# Restore completo de pg-core
cat /backups/pg_core/pg_core_20260517_120000.sql.gz | gunzip | docker exec -i pg-core psql -U postgres

# Restore de UNA database específica en pg-demos (ej: tienda_db)
docker exec pg-demos pg_dump -U postgres -d tienda_db | gzip > /tmp/tienda_db.sql.gz
# Luego en restore:
gunzip -c /tmp/tienda_db.sql.gz | docker exec -i pg-demos psql -U postgres -d tienda_db

# Restore de config
gpg --decrypt /backups/config/config_20260517_120000.tar.gz.gpg | tar xz -C /
```

### WAL Archiving + PITR (Fase 2 Roadmap):

`pg_dumpall` sirve al inicio, pero no escala. Roadmap para recovery más fino:

```
Fase 1 (hoy):   pg_dumpall cada 6h → RPO ≤ 6h, RTO ≤ 2h
Fase 2 (3-6 meses):
  └── WAL-G instalado
  └── WAL archiving continuo a Cloudflare R2
  └── RPO ≤ 1 minuto (point-in-time recovery)
  └── RTO ≤ 30 min (basebackup + WAL replay)
  └── `pg_dumpall` sigue como fallback semanal
Fase 3 (año+):
  └── Streaming replication a VPS secundario (warm standby)
  └── Failover manual documentado
  └── RTO ≤ 5 min
```

**Cuándo activar Fase 2:** cuando perder 6h de datos sea inaceptable para el negocio.
**Cuándo activar Fase 3:** cuando el negocio no pueda estar offline más de 5 minutos.

---

## 16. Estrategia de Seguridad

### Firewall (UFW):

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp              # SSH (rate-limited)
ufw allow 80/tcp              # HTTP
ufw allow 443/tcp             # HTTPS
ufw allow from {ADMIN_IP} to any port 8000  # Coolify admin
ufw enable
```

### Swap (obligatorio en CX43):

```bash
# 8GB swapfile — crítico para builds Node/Python y picos de RAM
fallocate -l 8G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# /etc/fstab:
/swapfile none swap sw 0 0

# vm.swappiness=10 (solo usa swap cuando realmente necesita)
echo "vm.swappiness=10" >> /etc/sysctl.conf
```

**Por qué:** Los 16GB del CX43 son nominales. En realidad:
- Linux page cache + Docker overlay comen ~1-2GB
- Postgres cache + conexiones comen ~1-2GB
- Un build de Next.js solo puede consumir 2-4GB temporalmente
- Swap evita OOM kills durante spikes

### Docker log rotation (evita llenar disco):

```yaml
# /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5"
  }
}
```

Sin esto, un container que loguea mucho puede llenar 160GB en horas.

### Secrets rotation:

```bash
# Convención de rotación:
#   {PROYECTO}_{PROPIEDAD}_V{version}
#
# Ejemplo:
#   WS_DB_PASS_V1  → primera versión
#   WS_DB_PASS_V2  → después de rotación
#   WS_DB_PASS     → alias al actual (Coolify lo resuelve)

# Política:
#   - Rotación cada 6 meses (obligatorio)
#   - Rotación inmediata si:
#     - Miembro del equipo se va
#     - Brecha de seguridad
#     - Secreto expuesto accidentalmente
#   - No compartir secrets entre proyectos
#   - Cada proyecto tiene su propio SECRET_KEY, DB_PASS, API_KEY

# En Coolify:
#   - Secrets marcados como "encrypted" (toggle)
#   - Audit log de quién accedió/qué cambió
#   - Backup de secrets solo en GPG cifrado offsite
```

### Docker image pruning (disco finito):

```cron
# /etc/cron.daily/docker-cleanup
0 3 * * * root docker image prune -a --filter "until=168h" -f
```

En 160GB, con deploys frecuentes a GHCR, las imágenes viejas se acumulan rápido.
Esta política limpia imágenes sin tag o no usadas en > 7 días.

### Disk budget (160GB NVMe):

Sin límites explícitos, el primer incidente serio será **disk full**. Budget recomendado:

| Recurso | Budget | Notas |
|---------|--------|-------|
| Docker images + layers | 20GB | `docker image prune -a` semanal |
| Logs (Docker + sistema) | 10GB | `max-size: 10m, max-file: 5` + rotación |
| Backups locales (pg_dump) | 30GB | Retención 14 días, comprimidos |
| Postgres data (pg-core + pg-demos) | 50GB | 2 instancias, shared_buffers + WAL |
| Observabilidad (Prometheus) | 20GB | Retención 15d, métricas de 15s |
| Overhead + temp + builds | 30GB | Builds Node, temp tables, overlay2 |
| **Total** | **160GB** | Ajustar cuando se ocupe > 80% |

**Alarma:** cuando cualquier categoría excede 80% de su budget o el disco total llega a 85% → alerta en Grafana.

### Hardening Checklist:

```
□ Firewall: solo 22, 80, 443, 8000(admin IP)
□ SSH: key-only, PasswordAuthentication no, fail2ban, rate-limit
□ Postgres: internal network only, sin puerto host
□ PgBouncer: internal network only, sin puerto host
□ Redis: internal network only, requirepass obligatorio
□ API: rate-limit por plan/tenant, CORS angosto, helmet headers
□ Web: CSP, X-Frame-Options: DENY, XSS-Protection, HSTS preload
□ Traefik: TLS 1.3 only, secure ciphers, HSTS
□ Cloudflare: WAF ON, Bot Fight Mode, Rate Limiting, Full SSL Strict
□ Secrets: Coolify env vars cifrados, nunca en repo
□ Container: non-root user (USER app en Dockerfile), read-only FS donde se pueda
□ Monitoring: Grafana con auth, Prometheus/Loki solo internal
□ Updates: unattended-upgrades seguridad, docker monthly
□ Docker: resource limits en todos los containers
```

### Dockerfile Seguro (ejemplo):

```dockerfile
FROM python:3.11-slim AS builder
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime
RUN addgroup --system --gid 1001 app \
 && adduser --system --uid 1001 app
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
USER app
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -fsS http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 17. CI/CD — GitHub Actions

### Template para cada proyecto:

```yaml
# .github/workflows/deploy.yml (en cada repo de proyecto)
name: Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  ORG: webshooks     # o argfy, o el que corresponda
  SERVICE_API: {proyecto}-api
  SERVICE_WEB: {proyecto}-web

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # Tests específicos del proyecto
      - run: echo "Tests placeholder"

  build:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [api, web]
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build & push ${{ matrix.service }}
        uses: docker/build-push-action@v6
        with:
          context: ./${{ matrix.service == 'api' && 'backend' || 'frontend' }}
          push: true
          tags: |
            ghcr.io/${{ env.ORG }}/${{ env.SERVICE_API || env.SERVICE_WEB }}:${{ github.sha }}
            ghcr.io/${{ env.ORG }}/${{ env.SERVICE_API || env.SERVICE_WEB }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Coolify deploy
        run: |
          curl -sS -X POST "${{ secrets.COOLIFY_DEPLOY_WEBHOOK }}" \
            -H "Authorization: Bearer ${{ secrets.COOLIFY_TOKEN }}"
```

### Pipeline completo:

```
PR → test
    └── fail → ❌

main push → test → build images → push to ghcr → trigger Coolify webhook
                                                   └── Coolify pull new images
                                                   └── docker compose up -d
                                                   └── healthcheck → green ✅
                                                   └── fail → rollback auto
```

### Excepciones:
- **Proyectos solo frontend** (luzguffantti, anamurat): matrix solo `[web]`
- **Proyectos con scheduler/worker**: agregar al matrix o usar mismo build que api con CMD diferente

---
## 19b. Migration Policy

Las migraciones de DB son la causa #1 de outage en proyectos en crecimiento. Reglas obligatorias:

```
Reglas de migración (obligatorio):

1. NUNCA hacer DROP + ADD en el mismo deploy
   └── Hacer: ADD columna → deploy código → DROP columna (expand/contract pattern)

2. Siempre backward-compatible
   └── El código nuevo debe funcionar con el schema viejo
   └── El código viejo debe funcionar con el schema nuevo (durante rolling update)

3. Índices CONCURRENTLY
   └── CREATE INDEX CONCURRENTLY (no bloquea escrituras)
   └── DROP INDEX CONCURRENTLY

4. Migraciones idempotentes
   └── IF NOT EXISTS / IF EXISTS
   └── Correr la misma migración 2 veces no debe romper nada

5. Rollback de migration documentado
   └── Cada migration debe tener su "down" definido
   └── Probado antes del deploy

6. Sin migraciones automáticas en startup
   └── Alembic migrate se corre como job separado (api-migrate)
   └── No en el healthcheck ni en el entrypoint del web server

7. Auditoría
   └── Tabla alembic_version con hash de revisión
   └── Log de migraciones en Sentry (success/fail)
```

### Build policy — evitar OOM en builds:

Los builds de Next.js y Node pueden consumir 2-4GB de RAM temporalmente. En 16GB nominales (~9GB reales), 2 builds simultáneos + Postgres + apps = OOM.

```yaml
# GitHub Actions: build REMOTO. VPS solo hace pull de imágenes ya buildadas.
# Esto evita que el VPS tenga que compilar.
#
# Si se builda LOCAL (en VPS):
#   - max 1 build concurrente por VPS
#   - Programar builds fuera de horas pico (ETL, scheduler)
#   - `NODE_OPTIONS="--max_old_space_size=2048"` para builds Node

# CI/CD: build en GitHub → push a GHCR → VPS solo pull
```

**Recomendación estricta:** buildear en GitHub Actions (remoto). El VPS solo hace `docker pull`. Si hay que buildear en el VPS (development), hacerlo serializado.

---
## 19c. Worker & Job Isolation

Los workers ETL, scrapers, cron jobs, y jobs de IA son los que más probablemente matan la VPS (CPU spikes, memory leaks, conexiones infinitas).

### Política de workers:

```
1. Worker queue por prioridad
   └── high queue: webhooks, API requests, time-sensitive
   └── low queue: ETL batch, scrapers, reports, IA
   └── Si low queue satura, high queue sigue respondiendo

2. Timeout obligatorio por job
   └── ETL: max 30 min
   └── Scraper: max 5 min
   └── IA/ML: max 60 min
   └── Si excede timeout → kill + log a Sentry

3. Max concurrency
   └── 1 worker ETL a la vez (serializado)
   └── 1 scraper a la vez (serializado)
   └── Múltiples webhooks en paralelo (rápidos, < 5s)

4. Dead letter queue
   └── Jobs que fallan 3 veces → a DLQ
   └── No reintentar infinitamente
   └── Notificar a Slack/Sentry

5. Worker container separado del scheduler
   └── scheduler: solo encola trabajos (liviano, 128MB RAM)
   └── worker: ejecuta trabajos (pesado, 512MB RAM)
   └── Escalar: `docker compose up -d --scale worker=2`
```

### Anti-patterns de workers:

| ❌ Error | 🔴 Consecuencia |
|----------|---------------|
| Worker dentro del mismo proceso que API | Un scraper lento bloquea requests HTTP |
| Sin timeout | Job infinito consume RAM hasta OOM |
| Reintento infinito | Job fallido satura logs + CPU + DB |
| Sin cola (ejecución directa) | Picos de carga matan Postgres |
| Un worker para todo | ETL batch bloquea webhook rápido |
| Sin límite de concurrencia | 10 scrapers en paralelo saturan 16GB |

---

| ❌ Error | 🔴 Consecuencia |
|----------|---------------|
| `DROP COLUMN` en mismo deploy que código nuevo | Rollback imposible |
| `ALTER TABLE` sin lock timeout | DB caída 30min en tablas grandes |
| Migración en entrypoint del container | 2 containers peleándose por la migration |
| `NOT NULL` agregado sin default | Error en filas existentes |
| Índice bloqueante en tabla de producción | Downtime para escrituras |
| Sin `down_revision` en Alembic | Rollback imposible |

---

## 18. Observabilidad

### Stack:

```
┌───────────────────────────────────────────────────────────┐
│                    Grafana (mon.webshooks.com)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │Dashboards│  │  Alerts   │  │  Logs    │  │  Traces   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬─────┘ │
│       │              │             │               │       │
│  ┌────▼─────┐  ┌─────▼─────┐ ┌────▼─────┐  ┌──────▼──────┐│
│  │Prometheus │  │Prometheus │ │   Loki   │  │   Sentry    ││
│  │(metrics)  │  │(alerts)   │ │(logs)    │  │(errors)     ││
│  └────┬─────┘  └───────────┘ └────┬─────┘  └──────┬──────┘│
│       │                            │                │       │
│  ┌────▼────────────────────────────▼────────────────▼───┐  │
│  │  node-exp │ cadvisor │ promtail │ API /metrics       │  │
│  │  + blackbox-exp (SSL checks)    │                    │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

### Business Metrics (Fase 2 — cuando haya tráfico real):

Las métricas de infraestructura son necesarias pero no suficientes. Las métricas de negocio son más importantes para decidir qué construir.

| Métrica de negocio | Fuente | Dashboard |
|--------------------|--------|-----------|
| DAU (daily active users) | API auth logs + Prometheus counter | **Business Overview** |
| Tenants activos | DB query (count distinct tenant_id) | **Business Overview** |
| Webhooks recibidos/min | API counter label `endpoint=webhooks` | **Business Overview** |
| Tasa de conversión (free → pro) | DB query (subscriptions) | **Conversion Funnel** |
| Errores por tenant | Sentry tag `tenant_id` | **Sentry Dashboard** |
| Uso por plan (requests/día) | API counter label `plan` | **Business Overview** |
| Feature usage (qué endpoints se usan) | API counter label `endpoint` | **Product Analytics** |
| Costo por tenant | (requests × avg_latency) + storage | **Cost Analytics** |

**Regla:** no implementar hasta que haya al menos 100 requests/día de usuarios reales. Las primeras métricas de negocio se ven con SQL + Sentry.

### Métricas esenciales por proyecto:

| Métrica | Fuente | Alerta si |
|---------|--------|-----------|
| CPU usage VPS | node-exporter | > 80% 5min |
| RAM usage VPS | node-exporter | > 85% |
| Disk usage | node-exporter | > 85% |
| API latency p99 | Prometheus (/metrics) | > 2s |
| API 5xx rate | Prometheus | > 1% en 5min |
| API requests/min | Prometheus | drop > 50% |
| Container restarts | cadvisor | cualquier restart |
| SSL expiry | blackbox-exporter | < 14 días |
| Sentry error rate | Sentry | > 10 eventos/min |
| Cada proyecto | labels `project={nombre}` | filtrable por proyecto |

### Grafana Dashboards:

| Dashboard | Propósito |
|-----------|-----------|
| **VPS Overview** | CPU/RAM/Disk/Network host |
| **Container Health** | Estado, restarts, resources por container |
| **API Performance (global)** | Latencia, throughput, error rate por proyecto |
| **Database Core** | Conexiones activas, query time, tamaño DBs |
| **Database Demos** | Ídem, filtrable por demo |
| **Business — webshooks** | Proyectos registrados, webhooks/min, tenants activos |
| **Scheduler** | ETL jobs, duración, success/fail rate |

### Logging:

```
Todos los containers → stdout/stderr
  └── Docker logs → Promtail los captura
       └── Loki los almacena (retención 7 días)
            └── Grafana los consulta

Labels en Loki por proyecto:
  - project=webshooks
  - project=argfy
  - project=tienda
  - service=api / service=web / service=scheduler
```

### Sentry:

```python
# Inicialización en cada backend
import sentry_sdk
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
    traces_sample_rate=0.1,
)
```

---

## 19. Estrategia de Despliegue

### Ambientes: producción + staging + preview

Cada proyecto debe tener al menos 2 ambientes en Coolify:

```
webshooks/
├── Production        → main branch, deploy automático
├── Staging           → staging branch, deploy automático
└── Preview           → PR branches, deploy on-demand (Coolify PR feature)

argfy/
├── Production        → main
├── Staging           → staging
└── Preview           → PR branches
```

**Staging** debe tener:
- Misma arquitectura que prod (Traefik, DB, Redis) pero con datos anonimizados
- API keys de prueba (MercadoPago sandbox)
- Sin webhooks reales
- Monitoreo separado (Sentry staging project)

**Costos:** en un solo VPS, staging comparte recursos con prod pero con `mem_limit` más restrictivos (ej: api-staging 128m vs api 256m). Alternativa futura: VPS separado para staging.

### Por proyecto, sin dependencias entre sí:

```
webshooks repo push main
  → build + push ghcr.io/webshooks/webshooks-api:git-abc123
  → Coolify webhook → pull + deploy webshooks-api
  → healthcheck → green ✅

tienda repo push main
  → build + push ghcr.io/webshooks/tienda-api:git-def456
  → Coolify webhook → pull + deploy tienda-api + tienda-web
  → healthcheck → green ✅
```

### Rolling update (Coolify default):

```
1. Pull new image
2. Start new container alongside old
3. Wait for healthcheck to pass
4. Route traffic to new container
5. Stop old container
```

### Zero-downtime requirements:

- Migraciones backward-compatible (add columns, never remove)
- API versioning (prefix /api/v1)
- Web no depende de API version exacta
- Scheduler: pausar jobs, migrar, reanudar

### Rollback:

```
Opción 1: Coolify rollback button → redeploy container anterior
Opción 2: GitHub revert PR → push → deploy automático
Opción 3: Manual → docker compose -f docker-compose.yml up -d con tag anterior
```

---

## 20. Estrategia de Escalabilidad Futura

### Fase 1 — Hoy (1 VPS CX43):

**Cálculo realista de RAM disponible:**

```
16GB nominal
  - 1.5GB Linux page cache + kernel
  - 1.0GB Docker overlay + containerd
  - 2.0GB Postgres (2 instancias: shared_buffers + cache)
  - 0.5GB PgBouncer (2 instancias)
  - 1.0GB Redis (RDB + AOF + working set)
  - 0.8GB Swap overhead + buffers
────────────────
  ~9.2GB libres para apps
```

**Con 9.2GB para apps:**
- webshooks-api (256m) + webshooks-web (256m) + webshooks-scheduler (128m) = 640MB
- argfy-api (512m) + argfy-web (256m) + argfy-scheduler (128m) = 896MB
- 7 demos × (256m api + 256m web) = 3,584MB
- Prometheus (256m) + Grafana (256m) + node-exporter (64m) + blackbox (32m) = 608MB
- Uptime Kuma (128m) = 128MB

**Total aproximado:** ~5.8GB apps + overhead = **dentro del margen**.

Builds de Next.js/Node pueden consumir 2-4GB temporales. Swap de 8GB (ver sección 16) evita OOM.

**Límite práctico:** ~15-20 containers medianos (cumpliendo `mem_limit`).

### Fase 2 — Crece (2 VPS):
```
VPS1 (CX43): webshooks + argfy + projects (pg-core)
VPS2 (CX31): demos (pg-demos)
Conexión: Tailscale / WireGuard entre VPSs
Nuevas networks Docker externas cross-VPS
```

### Fase 3 — Escala (3+ VPS):
```
VPS1: webshooks control plane + shared services (pg-core, redis)
VPS2: argfy + projects pesados
VPS3: demos
VPS4-N: demos específicos que escalan solos
```

### Costos estimados (2026):

| Servicio | Uso | Costo/mes |
|----------|-----|-----------|
| Hetzner CX43 | 4 vCPU · 16GB · 160GB NVMe | ~€16 |
| Cloudflare Free | CDN + WAF + SSL | €0 |
| Cloudflare R2 | 10GB backups offsite | ~$0.04 |
| Sentry (Team) | 50k eventos/mes | ~$0 (free tier) |
| GHCR (GitHub) | Container registry | €0 (free) |
| Coolify | Self-hosted | €0 |
| **Total** | | **~€16/mes** |

**Cuando escale:** el primer salto de costo será agregar un segundo VPS (~€8-16/mes).
El segundo salto será Sentry Team ($26/mes) o Grafana Cloud ($49/mes).

**Regla:** no pagar por observabilidad hasta que el producto genere revenue. Prometheus + Grafana self-hosted alcanzan.

### Fase 4 — Orquestación (futuro lejano):
```
Opción A: Docker Swarm (más simple, nativo)
Opción B: K3s (Kubernetes lightweight, más features)
Migración desde docker-compose usando stacks/compose specs
```

### La arquitectura actual ya soporta esta migración:

| Componente | Cómo facilita migración |
|------------|------------------------|
| Redes externas | `external: true` → conectar containers cross-VPS |
| Volúmenes nombrados | `docker volume create --driver ...` en otro nodo |
| Labels Traefik | Reenrutar tráfico cambiando IP destino |
| PgBouncer | Cambiar DATABASE_URL sin cambiar apps |
| Healthchecks | Swarm/K8s usa healthchecks nativos |
| Resource limits | `deploy.resources` es compatible con Swarm |

---

## 21. Anti-Patterns

| ❌ Error | 🔴 Problema | ✅ Alternativa |
|----------|------------|---------------|
| **Un solo Postgres para todo** | Query lento de un demo afecta webshooks | pg-core + pg-demos separados |
| **Un docker-compose monstruoso** | Imposible debuggear, escalar, mantener | Un compose por proyecto |
| **Sin resource limits** | Memory leak de un demo tumba todo el VPS | `deploy.resources.limits.memory` |
| **CORS demasiado abierto** | Cualquier web puede llamar tu API | CORS = dominios exactos |
| **Expone DB en puerto host** | Ataque directo a Postgres desde internet | DB solo en red internal |
| **Un solo network para todo** | Si comprometen un container, alcanzan todo | Redes separadas por capa |
| **Sin healthchecks** | Coolify/Traefik envían tráfico a servicio muerto | Healthcheck en cada container |
| **Imagen `:latest` en producción** | Rollback a versión exacta imposible | Tag con SHA + latest |
| **Secrets en docker-compose** | Filtrados en git o en CI logs | Coolify env vars cifrados |
| **Logs solo en stdout sin collector** | Se pierden al reiniciar container | Loki + Promtail |
| **`restart: always`** | Container en crash loop forever quema CPU | `restart: unless-stopped` |
| **Root inside container** | Si comprometen container, tienen root | `USER app` en Dockerfile |
| **Debug mode en producción** | Info sensible + stack traces expuestos | `DEBUG=false` siempre |
| **Sin rate limit** | Loop infinito o ataque DDoS te funde la API | Rate limit por tenant/IP |
| **Un compose con depends_on sin conditions** | Servicio arranca antes que la DB esté lista | `condition: service_healthy` |
| **Usar mismo tag para múltiples ambientes** | No sabés qué corre en prod vs staging | Tags diferenciados (env prefix) |

---

## 22. Checklist de Implementación

### Fase 0 — Provisionamiento
```
□ VPS Hetzner CX43 contratado (Ubuntu 24.04 LTS)
□ SSH key configurada, PasswordAuthentication no
□ UFW: solo 22, 80, 443, 8000(admin IP)
□ fail2ban instalado y configurado
□ unattended-upgrades configurado (solo security)
□ Docker + Docker Compose instalados
□ Coolify instalado (docker run)
□ Coolify configurado con dominio coolify.webshooks.com (o solo IP:8000)
□ Dominios en Cloudflare: proxy activo (naranja)
□ Cloudflare SSL: Full (strict), HSTS ON
```

### Fase 1 — Infraestructura Base
```
□ /infrastructure/ creado en VPS
□ docker-compose.yml desplegado (Traefik + Postgres + Redis + PgBouncer + Obs)
□ Traefik funcionando con Let's Encrypt
□ pg-core funcionando con databases iniciales
□ pg-demos funcionando
□ pgbouncer-core y pgbouncer-demos funcionando
□ redis-shared funcionando con requirepass
□ Prometheus recolectando métricas
□ Grafana accesible via mon.webshooks.com
□ Uptime Kuma configurado (status.webshooks.com)
□ Swap 8GB configurado + vm.swappiness=10
□ Docker log rotation configurado (10m × 5 archivos)
□ Docker image pruning automático (cron semanal)
□ Blackbox exporter monitoreando SSL/external endpoints
□ Staging compose + env configurados (misma VPS, resource limits reducidos)
□ Prometheus alertas configuradas (CPU, RAM, Disk, API)
□ Backups locales configurados y probados
□ Backups offsite configurados (R2/B2)
□ /infrastructure/ en repo infrastructure (backup de config)
```

### Fase 2 — webshooks.com
```
□ Repo webshooks creado
□ Dockerfile backend (FastAPI)
□ Dockerfile frontend (Next.js)
□ docker-compose.yml del proyecto
□ GitHub Actions CI/CD funcionando
□ Coolify project creado (webshooks-api, webshooks-web, webshooks-scheduler)
□ Primer deploy exitoso
□ Dominio webshooks.com apuntando
□ CORS configurado
□ Multi-tenancy con schemas implementado
□ Healthcheck funcionando
```

### Fase 3 — Demos
```
□ Repos creados (tienda, electronica, zapateria, clinica, instructor, yoga, trainer)
□ Cada repo con Dockerfile + CI/CD
□ docker-compose.yml por demo (ref: networks externas)
□ Coolify projects creados (api + web por demo)
□ Databases creadas en pg-demos (tienda_db, electronica_db, etc.)
□ Dominios *.webshooks.com apuntando (wildcard CNAME)
□ Traefik routers funcionando por subdominio
□ Cada demo deployada y funcionando
□ Healthchecks verdes
□ Resource limits configurados
```

### Fase 4 — Projects
```
□ argfy.com migrado/actualizado a la nueva arquitectura
□ luzguffantti.com deployado
□ anamurat.com deployado
□ CORS actualizados
□ SSL verdes
□ DNS configurado
```

### Fase 5 — Observabilidad + Operaciones
```
□ Grafana dashboards importados:
  □ VPS Overview
  □ Container Health
  □ API Performance (global, filtrable por proyecto)
  □ Database Core + Database Demos
  □ webshooks Business
□ Alertas configuradas en Grafana:
  □ CPU > 80%
  □ Disk > 85%
  □ API 5xx > 1%
  □ Container restart
  □ SSL < 14 días
□ Sentry DSNs configurados en cada backend
□ Backups probados (pg_restore verificado)
□ Runbook documentado en README del repo infrastructure
□ Al menos 2 personas saben hacer restore
```

---

## Template Rápido — Nuevo Proyecto (checklist para colaboradores)

Cuando un colaborador suma un proyecto nuevo al ecosistema:

```
1. Crear repo: github.com/{org}/{proyecto}
2. Agregar Dockerfile (backend y/o frontend)
3. Agregar .github/workflows/deploy.yml (template)
4. Elegir DB: pg-core (proyectos críticos) o pg-demos (demos)
5. Crear database en la instancia correspondiente
6. Crear proyecto en Coolify (api + web)
7. Configurar env vars en Coolify UI
8. Agregar dominio/subdominio en Cloudflare
9. Primer deploy → git push main
10. Agregar dashboard en Grafana (template)
11. Configurar alertas básicas
```

---

## 23. Correcciones Post-Review

Este plan fue revisado por un arquitecto DevOps senior. Las críticas y correcciones aplicadas:

### 23.1. ❌ VPS sobrecargada → ✅ Stack mínimo inicial

| Antes | Después |
|-------|---------|
| Loki + Promtail + cAdvisor desde el día 1 | Solo Prometheus + Grafana + node-exporter |
| ~2.5GB en observabilidad | ~500MB en observabilidad |
| Riesgo de OOM en builds + ETLs | Margen seguro para operación |

**Loki + cAdvisor se agregan en Fase 2** cuando haya RAM suficiente o necesidad real.
Por ahora: Sentry para errores, `docker compose logs -f` para debugging, Prometheus para métricas.

### 23.2. ❌ `deploy.resources` no funciona → ✅ `mem_limit` + `cpus`

`deploy.resources` es de Docker Swarm. En `docker compose` standalone se **ignora silenciosamente**. Reemplazado por `mem_limit` y `cpus` en todos los compose del plan.

### 23.3. ❌ Coolify + Traefik manual híbrido → ✅ Usar Traefik de Coolify

**Decisión final: NO desplegar Traefik manual.** Coolify tiene Traefik integrado que gestiona automáticamente:
- Routers por dominio
- Certificados Let's Encrypt
- Middleware (rate limit, headers, auth)

Los proyectos solo necesitan labels Traefik en sus `docker-compose.yml`. Coolify se encarga del resto.

Si en el futuro se necesita más control (ruteo avanzado, múltiples entrypoints), recién ahí considerar Traefik standalone.

### 23.4. ❌ Repo por demo → ✅ Monorepo si comparten stack

Agregada la opción de monorepo (`webshooks-demos/`) en sección 5 con Turborepo/pnpm workspace. Recomendado si 3+ demos comparten stack.

Cada demo en su propio repo solo si son stacks radicalmente diferentes.

### 23.5. ❌ Sin offsite backups → ✅ R2/Backblaze B2 agregado

Agregado `backup-offsite.sh` en sección 15 con rclone a Cloudflare R2 (~$0.36/GB/mes).
Mínimo obligatorio para no perder todo si la VPS muere.

### 23.6. ❌ Sin staging → ✅ Ambientes agregados

Agregada sección de ambientes (producción + staging + preview) en cada proyecto.
Staging comparte VPS con resource limits más restrictivos.

### 23.7. ❌ Observabilidad incompleta → ✅ Uptime Kuma + CrowdSec + Blackbox

Agregados a la infraestructura base:
- **Uptime Kuma** → status.webshooks.com (uptime monitoring simple, 128MB RAM)
- **CrowdSec** → seguridad colaborativa + bouncer para Traefik
- **Blackbox Exporter** → monitoreo de SSL, endpoints externos

### 23.8. ⚠️ Multi-tenant por schema — advertencia

Para **webshooks** funciona bien (pocos tenants, datos homogéneos).

Para **argfy** (finanzas), considerar `tenant_id column + row-level security` en vez de schemas si:
- Analytics pesados (joins cross-tenant)
- Reporting batch
- Warehouse futuro
- Migraciones complejas

**Decisión:** mantener schemas por ahora, reevaluar cuando argfy tenga > 50 tenants.

### 23.9. 🧹 Correcciones segunda ronda

| Cambio | Sección | Motivo |
|--------|---------|--------|
| Uptime Kuma: eliminado `ports:` | 12 | Está detrás de Traefik, no necesita puerto host |
| CrowdSec movido a Fase 2 (comentado) | 12 | Cloudflare ya cubre DDoS/bots/WAF. CrowdSec agrega complejidad temprana |
| Docker log rotation (`max-size: 10m`, `max-file: 5`) | 16 | Evita que logs llenen 160GB NVMe |
| Docker image pruning (cron: 7 días) | 16 | GHCR + deploys frecuentes llenan disco rápido |
| Swap 8GB + vm.swappiness=10 | 16 | Crítico para builds Node/Python en 16GB nominales (~9GB reales) |
| Migration Policy (expand/contract, no DROP same deploy) | 19b | #1 causa de outage en producción |
| RAM calculation realista (9.2GB libres, no 16GB) | 20 | Linux cache + Docker overlay + Postgres comen ~7GB |

### 23.10. 🧹 Correcciones tercera ronda (review final)

| Cambio | Sección | Motivo |
|--------|---------|--------|
| `infrastructure_public` eliminada | 12 | Traefik usa host ports 80/443. Red `internal: true` no tenía sentido. |
| Traefik manual eliminado del compose | 12 | Coolify provee Traefik built-in. No desplegar Traefik manual. Los labels en cada proyecto definen routing. |
| Grafana port corregido: 3001 → 3000 | 8, 12 | Grafana escucha en 3000 por defecto. |
| Traefik dashboard deshabilitado | 12 | Dashboard expuesto = riesgo. Solo con auth-basic si se necesita. |
| Secrets rotation policy | 16 | `_V1`, `_V2`, rotación 6 meses, postura ante breach |
| Disk budget table | 16 | 160GB dividido en 7 categorías con alerta al 80% |
| Build policy | 19 | Build remoto en CI. VPS solo pull. Si build local: serializado. |
| DR con RPO/RTO | 15 | RPO ≤ 6h, RTO ≤ 2h. Restore procedure en 8 pasos. |
| WAL archiving + PITR roadmap | 15 | Fase 2: WAL-G + PITR (RPO ≤ 1min). Fase 3: warm standby (RTO ≤ 5min). |
| Business metrics | 18 | DAU, conversiones, uso por plan, feature usage. No implementar hasta 100 req/día. |
| Worker & job isolation | 19c | Queues por prioridad, timeout obligatorio, max concurrency, dead letter queue |
| Cost tracking | 20 | ~€16/mes total. Primer salto: 2do VPS. |

### 23.11. Evaluación final de la guía

| Métrica | Score |
|---------|-------|
| Arquitectura | 9.4/10 |
| Operabilidad | 9.2/10 |
| Seguridad | 8.9/10 |
| Escalabilidad inicial | 9/10 |
| Complejidad vs valor | 9.5/10 |
| Riesgo operacional | Moderado-bajo |

| Métrica | Score |
|---------|-------|
| Arquitectura | 9.2/10 |
| Operabilidad | 9/10 |
| Escalabilidad | 8.9/10 |
| Simplicidad | 8.5/10 |
| Riesgo operacional | Moderado-bajo |

**Recomendación final:** Congelar la arquitectura de esta guía y empezar a desplegar proyectos reales con los colaboradores. Medir consumo real. Ajustar según incidentes reales, no teoría. El cuello de botella ahora es shipping, no infraestructura.

> "La próxima mejora importante no va a venir de más arquitectura en esta guía. Va a venir de incidentes reales, deploys reales, memoria real, tráfico real, fallos reales, backups reales, restore tests reales."

---

*Fin de la guía — Arquitectura DevOps para ecosistema webshooks.com*
