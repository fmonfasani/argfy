# Plan de Saneamiento — VPS Hetzner + Coolify (corto plazo)

> **Fecha:** 2026-05-17
> **Deadline operativo:** 2026-05-22 (entrega WebsHooks Consigna 4.0)
> **VPS:** Hetzner `89.167.96.239` (Ubuntu 24.04)
> **Coolify:** `https://coolify.webshooks.com`
> **Documento de referencia:** [`plan_devops_vps_opencode.md`](./plan_devops_vps_opencode.md)
> **Alcance:** Estabilizar el VPS y dejar funcionando argfy.com + 4 subdominios de colaboradores. Nada más.

---

## 0. Cómo se relaciona con `plan_devops_vps_opencode.md`

| Aspecto | plan_devops (norte) | plan_saneamiento (este) |
|---|---|---|
| Horizonte | Meses | 5-10 días |
| Estado asumido | VPS limpia | VPS con nginx host + containers sin orden |
| Cobertura | 7 demos, Loki, PgBouncer, R2, CrowdSec, staging | 4 colaboradores + argfy. Sin observabilidad ni staging. |
| Naming | §3 plan_devops | **Se respeta** (`{proyecto}-{rol}`) |
| Proxy | Traefik de Coolify (§23.3 plan_devops) | **Se respeta**. Decomisionar nginx host es el primer paso. |
| Redes | 6 redes (frontend/backend/db_core/db_demos/cache/obs) | **1 red** (`coolify` external) — simplificación temporal |
| Postgres | pg-core + pg-demos + PgBouncer | **1 Postgres por proyecto** (existente) — postergar consolidación |
| Backups | R2 + GPG + WAL archiving | **Snapshot Hetzner semanal** — postergar el resto |
| Observabilidad | Prometheus + Grafana + Uptime Kuma + Blackbox | **Sentry DSN** únicamente |

**Regla:** todo lo que este plan posterga queda agendado como `Fase ulterior → plan_devops_vps_opencode.md §{n}` para retomarlo cuando los 5 dominios estén verdes.

---

## 1. Objetivo y no-objetivo

### Objetivo (debe estar verde el 2026-05-22)

1. **argfy.com / www.argfy.com / api.argfy.com** sirven HTTPS desde Traefik de Coolify, no desde nginx host.
2. **zapateria.webshooks.com**, **forrajeria.webshooks.com**, **tienda.webshooks.com**, **electronica.webshooks.com** sirven HTTPS desde Traefik de Coolify.
3. Los 4 colaboradores tienen acceso a Coolify y pueden redeplotar su propio proyecto sin tocar lo ajeno.
4. Los containers existentes están renombrados según la convención del plan_devops §3.
5. Hay un snapshot Hetzner del VPS antes de tocar nada, y otro al cierre.

### No-objetivo (postergado a plan_devops)

- pg-core / pg-demos consolidados — cada proyecto sigue con su Postgres por ahora
- PgBouncer
- Prometheus + Grafana + Loki + Uptime Kuma
- Cloudflare proxy (sigue con A record directo de Namecheap)
- Backups offsite R2/B2
- Staging environments
- WAL archiving / PITR
- CrowdSec
- Monorepo de demos
- Migración de DNS a Cloudflare

---

## 2. Estado actual confirmado (audit)

> Detectado por SSH al VPS el 2026-05-17 antes de redactar este plan.

```
Proxy 80/443:        nginx 1.24.0 (apt, host) — interceptando todo
Coolify Traefik:     existe la red `coolify`, pero NO hay container proxy corriendo
Scripts huérfanos:   /root/_vps_nginx_switch_apex.sh, _vps_deploy_landing.sh,
                     _vps_probe_login.sh, _vps_reset_admin_pass.sh, _vps_set_auth_secrets.sh
Containers vivos:    argfy-backend, argfy-frontend, argfy-postgres,
                     romachic, forrajeria*, luzguffanti, zapateria,
                     app-db, app-web,
                     webshooks_backend_agents, webshooks_saas, webshooks_frontend,
                     coolify, coolify-db, coolify-redis, coolify-realtime
DNS Namecheap:       argfy.com, www.argfy.com, api.argfy.com → 89.167.96.239
                     *.webshooks.com → 89.167.96.239 (verificar wildcard)
```

\* `forrajeria` puede ya existir como container o no — se valida en Fase 1.

**Diagnóstico:** el nginx del host bypassa Coolify completamente. Mientras esté ahí, las labels Traefik en los compose no surten efecto.

---

## 3. Convenciones que aplicamos (subset del plan_devops §3)

```
Containers:
  argfy-backend          → argfy-api
  argfy-frontend         → argfy-web
  argfy-postgres         → argfy-db
  zapateria              → zapateria-web   (+ zapateria-api si existe)
  forrajeria             → forrajeria-web  (+ forrajeria-api si existe)
  tienda                 → tienda-web      (+ tienda-api si existe)
  electronica            → electronica-web (+ electronica-api si existe)

Coolify Projects:
  argfy                  → recursos argfy-*
  ws-zapateria           → recursos zapateria-*
  ws-forrajeria          → recursos forrajeria-*
  ws-tienda              → recursos tienda-*
  ws-electronica         → recursos electronica-*

DNS de colaboradores (Namecheap, A record → 89.167.96.239):
  zapateria.webshooks.com         (Mateo)
  forrajeria.webshooks.com        (Valentino)
  tienda.webshooks.com            (Aldana)
  electronica.webshooks.com       (Joaquin)
```

**Diferido a plan_devops:** redes `infrastructure_*`, volúmenes con prefijo, GHCR org structure, `pg-core` consolidado.

**Red Docker única por ahora:** `coolify` (external) — la que Traefik de Coolify usa. Es el `infrastructure_frontend` en versión simplificada.

---

## 4. Fase 0 — Safety net (30 min)

```
□ Snapshot Hetzner del VPS                  → consola Hetzner → "Take snapshot"
□ Coolify → Settings → Export configuration → guardar JSON en disco local
□ Listar DNS Namecheap actual (screenshot)  → registro de verdad antes de tocar
□ Listar containers + redes actuales:
    docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}' > ~/_audit_before.txt
    docker network ls > ~/_audit_networks.txt
    systemctl status nginx > ~/_audit_nginx.txt
□ Confirmar contenido de los _vps_*.sh:
    head -50 /root/_vps_*.sh > ~/_audit_scripts.txt
```

**Gate:** no avanzar a Fase 1 sin snapshot Hetzner confirmado (timestamp visible).

---

## 5. Fase 1 — Decomisionar nginx del host (1-2h, ventana de bajada)

> **Riesgo:** alto. Es el cambio que sí puede tirar todos los dominios. Por eso va con snapshot previo.

### 5.1. Mapear qué sirve hoy el nginx del host

```
□ ls /etc/nginx/sites-enabled/                → cada archivo = un dominio
□ Para cada archivo, anotar:
    - server_name
    - proxy_pass o root
    - listen 80 / listen 443
    - ssl_certificate path (probablemente Let's Encrypt)
□ Si hay vhost que NO esté en la lista de dominios objetivo (argfy.com, *.webshooks.com),
  preguntar a Federico antes de borrar. Posibles candidatos:
    - landing webshooks.com (puede o no estar en container)
    - login.webshooks.com (scripts _vps_set_auth_secrets.sh, _vps_reset_admin_pass.sh sugieren un auth gateway)
    - cualquier subdominio de clientes viejos
```

### 5.2. Decisión por cada vhost

| Vhost actual en nginx host | Acción |
|---|---|
| Sirve container ya gestionado por Coolify | Mover a Traefik (Fase 2-3) |
| Sirve landing estático/HTML directo | Migrar a container `webshooks-web` o desactivar |
| Sirve auth/login custom (`_vps_set_auth_secrets.sh`) | **PREGUNTAR antes de tocar** — puede ser crítico |
| Sirve algo desconocido | Listar y consultar antes de borrar |

### 5.3. Apagar nginx (solo cuando 5.1 y 5.2 estén resueltos)

```bash
systemctl stop nginx
systemctl disable nginx
# NO desinstalar todavía. Solo deshabilitado, por si hay que volver atrás:
# systemctl enable nginx && systemctl start nginx
```

### 5.4. Verificar que los puertos 80/443 quedan libres

```bash
ss -tlnp | grep -E ':(80|443) '   # debe estar vacío después del stop
```

**Gate:** no avanzar a Fase 2 si algún vhost no se entendió. El miedo correcto es: "no sé qué hace este `.conf` → no lo borro hoy".

---

## 6. Fase 2 — Activar Traefik de Coolify (30-60 min)

Por la decisión del plan_devops §23.3: usamos el Traefik built-in de Coolify, no instalamos uno propio.

```
□ Coolify UI → Server → hetzner → Proxy → seleccionar "Traefik v2" → Start
□ Esperar que el container `coolify-proxy` (o nombre equivalente) aparezca:
    docker ps | grep -i traefik
□ Verificar que se ata a 80/443:
    ss -tlnp | grep -E ':(80|443) '   # ahora debe mostrar el proceso de Traefik / Docker
□ Verificar la red `coolify` está activa:
    docker network inspect coolify | grep -A2 Containers
□ Probar Let's Encrypt con un dominio test (ej: redeploy argfy):
    curl -sI https://argfy.com  # debería traer cert válido emitido por Let's Encrypt, no nginx 403
```

**Gate:** `curl -sI https://argfy.com` devuelve `server: Traefik` (o equivalente) y cert con CN correcto. Si sigue saliendo `Server: nginx/1.24.0`, retroceder a Fase 1.

---

## 7. Fase 3 — Saneamiento de containers existentes (2-3h)

Por cada proyecto vivo en el VPS, aplicar este checklist. **Orden recomendado:** primero `argfy` (más prioritario), después los 4 de colaboradores, al final `romachic / luzguffanti / app-* / webshooks_*` (auditar si siguen vivos o se archivan).

### 7.1. Plantilla por proyecto

```yaml
# Aplicable a cada docker-compose de proyecto (en Coolify UI)
services:
  api:                       # o web según sea
    container_name: {proyecto}-{rol}     # zapateria-web, argfy-api, etc.
    restart: unless-stopped
    networks:
      - default
      - coolify              # red EXTERNAL — la que ve Traefik
    labels:
      - traefik.enable=true
      - traefik.docker.network=coolify
      - traefik.http.routers.{proyecto}-{rol}.rule=Host(`{dominio}`)
      - traefik.http.routers.{proyecto}-{rol}.entrypoints=https
      - traefik.http.routers.{proyecto}-{rol}.tls=true
      - traefik.http.routers.{proyecto}-{rol}.tls.certresolver=letsencrypt
      - traefik.http.services.{proyecto}-{rol}.loadbalancer.server.port={puerto-interno}

networks:
  default:
  coolify:
    external: true
```

### 7.2. Checklist por proyecto

```
□ Container renombrado a {proyecto}-{rol} (plan_devops §3.1)
□ Labels Traefik actualizadas con dominio correcto (plan_devops §7)
□ Red `coolify` external agregada al compose
□ Variables de entorno en Coolify UI (no en repo, no en compose)
□ Redeploy → docker ps muestra el container con el nombre nuevo
□ curl -sI https://{dominio}/ devuelve 200/3xx con cert Let's Encrypt
□ Sin tráfico cruzado: curl con Host header de otro proyecto NO sirve este
```

### 7.3. Orden de migración

| # | Proyecto | Dominio | Bloquea a |
|---|---|---|---|
| 1 | argfy | argfy.com, www.argfy.com, api.argfy.com | Nada — empezar acá |
| 2 | ws-zapateria | zapateria.webshooks.com | Onboarding Mateo |
| 3 | ws-forrajeria | forrajeria.webshooks.com | Onboarding Valentino |
| 4 | ws-tienda | tienda.webshooks.com | Onboarding Aldana |
| 5 | ws-electronica | electronica.webshooks.com | Onboarding Joaquin |
| 6 | (auditar) romachic, luzguffanti, app-*, webshooks_* | varios | No bloquea entrega |

**Para el punto 6**, hacer inventario rápido y decidir: ¿sigue activo? ¿lo archivo? ¿lo dejo correr sin label hasta después del 22?

**Gate por proyecto:** los 6 checks de §7.2 verdes antes de pasar al siguiente.

---

## 8. Fase 4 — Onboarding de los 4 colaboradores (1-2h)

### 8.1. Usuarios Coolify

```
□ Coolify → Settings → Team → Invite member para cada uno:
    - mateo@... → Project access: ws-zapateria (read+write), resto: none
    - valentino@... → Project access: ws-forrajeria
    - aldana@... → Project access: ws-tienda
    - joaquin@... → Project access: ws-electronica
□ Confirmar que NO tienen acceso a argfy ni a Settings de servidor
□ Federico queda como único Admin del Team
```

### 8.2. DNS Namecheap

```
□ Verificar A record para cada subdominio:
    zapateria.webshooks.com   A  89.167.96.239
    forrajeria.webshooks.com  A  89.167.96.239
    tienda.webshooks.com      A  89.167.96.239
    electronica.webshooks.com A  89.167.96.239
□ Si ya hay un wildcard *.webshooks.com → confirmar que no choca con vhosts viejos del nginx host
□ TTL = 300 durante la migración. Después: 3600.
```

### 8.3. Repos GitHub

Cada colaborador tiene su repo bajo `github.com/fmonfasani` (o donde estén actualmente). Para esta fase:

```
□ Confirmar que cada repo tiene:
    - Dockerfile funcionando (build local pasa)
    - docker-compose.coolify.yml con la plantilla §7.1
    - .env.example (sin secrets)
    - README mínimo con: dominio, cómo deployar, contacto
□ Federico es Maintainer; el colaborador es Write.
□ Webhook Coolify configurado en Settings → Webhooks del repo.
```

**Diferido a plan_devops §5:** orgs separadas en GitHub, templates compartidos, monorepo, GHCR.

### 8.4. Mensaje a los colaboradores (template)

```
Asunto: WebsHooks — acceso a Coolify y deploy de tu subdominio

1) Te invité a Coolify (mail aparte). Solo ves tu proyecto.
2) Tu dominio: {sub}.webshooks.com. Ya está apuntado al VPS.
3) Para redeplotar: push a main → Coolify lo agarra solo.
4) Para variables de entorno: panel Coolify → tu proyecto → Environment Variables.
   NUNCA commitearlas al repo.
5) Si algo no funciona: avisame antes de tocar config de proxy/networks.

Deadline entrega Consigna 4.0: 2026-05-22.
```

---

## 9. Fase 5 — argfy.com en producción (1-2h)

Aprovecha que la Fase 3 ya migró el compose. Quedan tareas específicas de argfy:

```
□ Cargar data_export en argfy-db (docker cp + psql)
□ Setear secrets reales en Coolify UI:
    - MP_ACCESS_TOKEN (Mercado Pago producción)
    - SENTRY_DSN (proyecto argfy en sentry.io)
    - COOLIFY_WEBHOOK_URL (la copia del Coolify UI)
□ GitHub Actions secrets:
    - COOLIFY_WEBHOOK_URL
    - COOLIFY_WEBHOOK_TOKEN
□ Smoke test end-to-end:
    - https://argfy.com/                            (landing)
    - https://argfy.com/login (Google OAuth)
    - https://api.argfy.com/health                  (FastAPI alive)
    - https://api.argfy.com/api/v1/screener         (datos cargados)
    - https://www.argfy.com/                        (redirect a apex)
□ Verificar cert: openssl s_client -connect argfy.com:443 -servername argfy.com
□ Test webhook MP: Mercado Pago → sandbox → ping a https://api.argfy.com/webhooks/mp
```

**Tests CI rotos (test_auth, test_fundamentals, test_main, test_ratios):** quedan como issue separado. **No bloquean** este saneamiento. Se atacan después del 22-may.

---

## 10. Acceptance checklist (gate de cierre)

El plan está completo cuando TODO esto está verde:

```
Proxy:
□ Único proceso escuchando 80/443: Traefik de Coolify
□ nginx del host: stopped + disabled (no removido todavía)

Dominios:
□ https://argfy.com               → 200, cert válido, Server: Traefik
□ https://www.argfy.com           → 301 a https://argfy.com
□ https://api.argfy.com           → /health = 200
□ https://zapateria.webshooks.com → 200
□ https://forrajeria.webshooks.com → 200
□ https://tienda.webshooks.com    → 200
□ https://electronica.webshooks.com → 200

Containers:
□ Nombrados según plan_devops §3.1: {proyecto}-{rol}
□ Todos los con dominio público están en la red `coolify` external
□ Ninguno expone puertos al host excepto Coolify y Traefik

Colaboradores:
□ 4 invitaciones Coolify aceptadas
□ Cada uno puede ver SOLO su proyecto
□ Federico único Admin

Seguridad mínima:
□ Snapshot Hetzner anterior al cambio: existe
□ Snapshot Hetzner posterior al cierre: existe
□ DNS Namecheap: solo los 7 registros del §3 + lo que pertenezca a otros proyectos auditados
□ Sentry DSN configurado en argfy (errores de prod visibles)

Documentación:
□ ~/audit_before.txt y ~/audit_after.txt en el VPS
□ Lista de _vps_*.sh con decisión por cada uno (mantener / borrar / migrar)
□ README en cada repo de colaborador con instrucciones de deploy
```

---

## 11. Runbook — comandos frecuentes durante la migración

```bash
# Ver qué container sirve un dominio (después de Fase 2)
docker exec coolify-proxy traefik show config | grep -A3 {dominio}

# Reiniciar Traefik de Coolify (si labels nuevas no aparecen)
docker restart coolify-proxy

# Forzar redeploy de un proyecto desde Coolify UI
Coolify → Project → Service → Restart / Redeploy

# Ver logs de Traefik en vivo
docker logs -f coolify-proxy 2>&1 | grep -E '(error|TLS|{dominio})'

# Verificar cert de un dominio
echo | openssl s_client -connect {dominio}:443 -servername {dominio} 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates

# Test rápido de routing por Host header
curl -sI -H "Host: argfy.com" http://89.167.96.239/
curl -sI https://argfy.com/

# Backup express de un Postgres antes de tocarlo
docker exec {proyecto}-db pg_dumpall -U postgres | gzip > ~/{proyecto}_$(date -u +%Y%m%d_%H%M%S).sql.gz

# Restaurar
gunzip -c ~/{proyecto}_*.sql.gz | docker exec -i {proyecto}-db psql -U postgres

# Listar containers que NO están en la red coolify
docker ps --format '{{.Names}}' | while read n; do
  docker inspect "$n" --format '{{.Name}} {{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' \
    | grep -v coolify
done
```

---

## 12. Riesgos y rollback

| Riesgo | Probabilidad | Mitigación | Rollback |
|---|---|---|---|
| Apagar nginx tira un dominio no auditado | Media | Fase 5.1 exhaustiva antes de stop | `systemctl start nginx` (queda solo disabled, no removido) |
| Cert Let's Encrypt rate-limited (5 fallos/h) | Baja | Probar con 1 dominio antes de migrar 5 | Esperar 1h, no forzar |
| Renombrar container rompe red interna | Media | Cambiar 1 servicio a la vez, no todo el compose junto | Volver al `container_name` previo en compose |
| Colaborador rompe config de su proyecto | Media | Permisos Coolify acotados a su Project | Federico tiene Admin global |
| data_export corrompido al cargar | Baja | pg_dumpall del estado actual antes de cargar | Restore desde backup express §11 |
| Snapshot Hetzner inutilizable | Muy baja | Tomar 2 snapshots (antes + en medio) | — |

**Punto sin retorno:** desinstalar `nginx` con apt. **Hasta el final de la entrega (22-may) NO desinstalar**, solo `stop + disable`.

---

## 13. Después del 22-may — handoff a `plan_devops_vps_opencode.md`

Cuando los 5 dominios estén verdes, retomar `plan_devops_vps_opencode.md` en este orden:

1. **§22 Fase 1 — Infraestructura base**: agregar Prometheus + Grafana + node-exporter (sin Loki todavía)
2. **§15 Backups**: cron de pg_dumpall + offsite a R2/B2
3. **§19 Staging**: ambiente staging para argfy primero
4. **§10 PgBouncer + pg-core/pg-demos**: consolidación de Postgres (cuando haya tiempo de migración)
5. **§17 CI/CD GitHub Actions**: completar pipeline con matrix build
6. **§16 Hardening**: ufw, fail2ban, swap 8GB, log rotation
7. **§23.7 Uptime Kuma + Blackbox**: monitoreo público

**Cuándo migrar a Cloudflare:** cuando aparezca el primer indicio de abuso (scraping pesado, intento DDoS, geo-blocking necesario). No antes — agrega complejidad sin valor inmediato.

---

## 14. Lo que NO entra acá (referencia rápida)

| Tema | Postergado a |
|---|---|
| pg-core + pg-demos consolidados | plan_devops §10 |
| PgBouncer | plan_devops §10 |
| Prometheus / Grafana / Loki / Uptime Kuma | plan_devops §12, §18 |
| Cloudflare proxy + WAF | plan_devops §7 |
| Backups offsite R2/B2 + WAL archiving | plan_devops §15 |
| Staging + preview environments | plan_devops §19 |
| CrowdSec | plan_devops §12 (Fase 2 comentado) |
| Monorepo de demos | plan_devops §5 |
| Resource limits (`mem_limit`, `cpus`) | plan_devops §13, §16 |
| Migration policy (expand/contract) | plan_devops §19b |
| Worker isolation + queues | plan_devops §19c |
| Multi-tenant schemas en webshooks | plan_devops §14, §23.8 |
| Migración de DNS Namecheap → Cloudflare | plan_devops §7 |
| Borrar nginx del host con apt | después del 2026-06-01 (un mes de gracia desde §13) |

---

*Fin del plan de saneamiento — retomar `plan_devops_vps_opencode.md` después del 22-may.*
