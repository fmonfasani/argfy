# Valentino Picco — forrajeria.webshooks.com

| Dato | Valor |
|------|-------|
| Colaborador | Valentino Picco |
| Tema | forrajeria |
| Dominio | `forrajeria.webshooks.com` |
| API | `api.forrajeria.webshooks.com` |
| Containers | `forrajeria-db`, `forrajeria-api`, `forrajeria-web` |
| Coolify Project | `ws-forrajeria` |
| Deadline | 2026-05-22 |

---

## Acceso

1. Revisá tu email — recibiste invitación a Coolify (`https://coolify.webshooks.com`)
2. Aceptala y creá tu contraseña
3. Solo ves tu proyecto `ws-forrajeria` — no podés ver otros proyectos ni config del servidor

## Tu dominio

`forrajeria.webshooks.com` ya apunta al VPS. Cuando deployes, Traefik emite SSL automáticamente via Let's Encrypt.

## Cómo deployar

Push a `main` en tu repo → GitHub webhook dispara deploy en Coolify automáticamente.

O desde Coolify UI:
1. Coolify → `ws-forrajeria` → servicio → "Deploy"
2. Esperar que el build termine (log visible en tiempo real)

## Instanciar el template del compose

```bash
# Copiar el template:
cp argfy/deployment/coolify/docker-compose.coolify.template.yml \
   deployment/docker-compose.coolify.yml

# Reemplazar placeholders (forrajeria + forrajeria.webshooks.com):
sed -i 's/{proyecto}/forrajeria/g; s/{dominio}/forrajeria.webshooks.com/g' \
   deployment/docker-compose.coolify.yml

# Verificar:
grep -n '{proyecto}\|{dominio}' deployment/docker-compose.coolify.yml   # debe estar vacío
```

Commitear el resultado, NO el template con placeholders.

## Variables de entorno

Setealas en Coolify UI → `ws-forrajeria` → Environment Variables. NUNCA en el repo.

Mínimas requeridas:
- `POSTGRES_DB=forrajeria`
- `POSTGRES_USER=forrajeria`
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
