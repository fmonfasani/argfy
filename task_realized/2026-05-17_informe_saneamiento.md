# Informe de Saneamiento — 2026-05-17

> **Fuente:** `plan/plan_saneamiento.md`
> **VPS:** Hetzner `89.167.96.239` — sin acceso SSH en esta sesión
> **Alcance:** Solo cambios locales sobre el repo en `D:\Software Development\Porfolio\valuarty`

---

## Resumen

Se aplicaron cambios locales sobre `argfy/deployment/docker-compose.coolify.yml` y se crearon 3 templates en `argfy/deployment/coolify/`. Las tareas que requieren SSH al VPS, Coolify UI, o Namecheap quedan pendientes.

---

## Cambios aplicados

### 1. `docker-compose.coolify.yml`

| Cambio | Antes | Después |
|--------|-------|---------|
| `container_name` en postgres | ausente | `argfy-db` |
| `container_name` en backend | ausente | `argfy-api` |
| `container_name` en frontend | ausente | `argfy-web` |
| Router label backend | `argfy-backend` | `argfy-api` |
| Router label frontend | `argfy-frontend` | `argfy-web` |
| Healthcheck backend | ausente | curl `localhost:8000/health` |
| Healthcheck frontend | ausente | wget `localhost:3000/` |

Service names (`postgres`, `backend`, `frontend`) se mantienen para no romper la resolución DNS interna de Docker. Solo se agregó `container_name:`.

### 2. Templates creados en `argfy/deployment/coolify/`

| Archivo | Propósito |
|---------|-----------|
| `docker-compose.coolify.template.yml` | Template parametrizado `{proyecto}`/`{dominio}` para colaboradores |
| `README.colaborador.md` | Instrucciones de deploy para los 4 colaboradores |
| `argfy.secrets.template.md` | Lista de variables de entorno a setear en Coolify UI para argfy |

### 3. Archivos preexistentes (no tocados)

`backend.env.example`, `frontend.env.example`, `postgres.env.example`, `secrets.env` — ya existían del 2026-05-16, no se modificaron.

---

## Estado actual por fase del plan

### Fase 0 — Safety net

| Tarea | Estado |
|-------|--------|
| Snapshot Hetzner | ⏳ Pendiente (consola Hetzner) |
| Export Coolify config | ⏳ Pendiente (Coolify UI) |
| Listar DNS Namecheap | ⏳ Pendiente (Namecheap) |
| Audit containers VPS | ⏳ Pendiente (SSH) |

### Fase 1 — Decomisionar nginx host

Requiere SSH al VPS. No se tocó.

### Fase 2 — Activar Traefik Coolify

Requiere Coolify UI. No se tocó.

### Fase 3 — Saneamiento containers

**Argfy** (local): ✅ `container_name:` y healthchecks aplicados.
**Argfy** (VPS): ⏳ Pendiente redeploy.
**Colaboradores** (4): ⏳ Pendiente.

### Fase 4 — Onboarding colaboradores

⏳ Pendiente (Coolify UI + Namecheap + GitHub).

### Fase 5 — argfy.com en producción

⏳ Pendiente (secrets + data_export + smoke tests).

---

## Lo que no se tocó (postergado a plan_devops)

- pg-core / pg-demos consolidados
- PgBouncer
- Prometheus / Grafana / Loki / Uptime Kuma
- Cloudflare proxy + WAF
- Backups offsite
- Staging environments
- CrowdSec
- Resource limits

---

*Fin del informe — 2026-05-17. Solo cambios locales. Pendientes: SSH al VPS + Coolify UI + Namecheap.*
