# Aldana Oviedo — tienda.webshooks.com

| Dato | Valor |
|------|-------|
| Colaboradora | Aldana Oviedo |
| Tema | tienda |
| Dominio | `tienda.webshooks.com` |
| API | `api.tienda.webshooks.com` |
| Containers | `tienda-db`, `tienda-api`, `tienda-web` |
| Coolify Project | `ws-tienda` |
| Deadline | 2026-05-22 |

---

## Acceso

1. Revisá tu email — recibiste invitación a Coolify (`https://coolify.webshooks.com`)
2. Aceptala y creá tu contraseña
3. Solo ves tu proyecto `ws-tienda` — no podés ver otros proyectos ni config del servidor

## Tu dominio

`tienda.webshooks.com` ya apunta al VPS. Cuando deployes, Traefik emite SSL automáticamente via Let's Encrypt.

## Cómo deployar

Push a `main` en tu repo → GitHub webhook dispara deploy en Coolify automáticamente.

O desde Coolify UI:
1. Coolify → `ws-tienda` → servicio → "Deploy"
2. Esperar que el build termine (log visible en tiempo real)

## Instanciar el template del compose

```bash
# Copiar el template:
cp argfy/deployment/coolify/docker-compose.coolify.template.yml \
   deployment/docker-compose.coolify.yml

# Reemplazar placeholders (tienda + tienda.webshooks.com):
sed -i 's/{proyecto}/tienda/g; s/{dominio}/tienda.webshooks.com/g' \
   deployment/docker-compose.coolify.yml

# Verificar:
grep -n '{proyecto}\|{dominio}' deployment/docker-compose.coolify.yml   # debe estar vacío
```

Commitear el resultado, NO el template con placeholders.

## Variables de entorno

Setealas en Coolify UI → `ws-tienda` → Environment Variables. NUNCA en el repo.

Mínimas requeridas:
- `POSTGRES_DB=tienda`
- `POSTGRES_USER=tienda`
- `POSTGRES_PASSWORD` (encrypted — generar con `openssl rand -hex 32`)
- `SECRET_KEY` (encrypted)
- `SENTRY_DSN` (opcional)

## Stack

- Frontend en puerto 3000
- API en puerto 8000
- Healthcheck en `/health` (API) y `/` (web)
- No exponer puertos al host

## Si algo no funciona

1. Coolify → Logs del servicio
2. Verificá que las env vars están seteadas
3. Avisame antes de tocar proxy, networks o firewall
