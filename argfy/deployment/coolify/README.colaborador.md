# Deploy en Coolify — Colaboradores WebsHooks

## Acceso

1. Revisá tu email — recibiste una invitación a Coolify (dominio: `https://coolify.webshooks.com`)
2. Aceptala y creá tu contraseña
3. Solo ves tu proyecto — no podés ver otros proyectos ni config del servidor

## Tu dominio

| Proyecto | Dominio |
|----------|---------|
| _depende_ | `{subdominio}.webshooks.com` |

Ya apunta al VPS. Cuando deployes, Traefik emite el certificado SSL automáticamente via Let's Encrypt.

## Cómo deployar

Push a `main` en tu repo → GitHub webhook dispara deploy en Coolify automáticamente.

O desde Coolify UI:
1. Coolify → tu proyecto → servicio → "Deploy"
2. Esperar que el build termine (log visible en tiempo real)

## Variables de entorno

**NUNCA las commitees al repo.** Se setean en Coolify UI:
1. Coolify → Proyecto → Environment Variables
2. Agregar cada variable y marcar como "encrypted" si es secreta
3. Redeploy después de cambiar

Las variables necesarias están documentadas en `deployment/coolify/backend.env.example` y `frontend.env.example`.

## Instanciar el template del compose

El archivo `docker-compose.coolify.template.yml` tiene placeholders `{proyecto}` y `{dominio}`. Reemplazalos por tus valores antes de usarlo:

```bash
# Desde la raíz de tu repo, copiá el template a tu deployment y reemplazá
cp argfy/deployment/coolify/docker-compose.coolify.template.yml \
   deployment/docker-compose.coolify.yml

# Reemplazo (ajustá {proyecto} y {dominio} a los tuyos):
sed -i 's/{proyecto}/zapateria/g; s/{dominio}/zapateria.webshooks.com/g' \
   deployment/docker-compose.coolify.yml

# Verificar que no queden placeholders sueltos:
grep -n '{proyecto}\|{dominio}' deployment/docker-compose.coolify.yml   # debe estar vacío
```

`{proyecto}` y `{dominio}` son strings literales (no env vars de Docker). El `sed` los reescribe en el archivo. Hacer esto **una sola vez** y commitear el resultado al repo, no el template con placeholders.

## Stack permitido

Cada proyecto define su propio Dockerfile. No hay restricción técnica de stack.

Reglas:
- El frontend debe responder en el puerto 3000
- La API debe responder en el puerto 8000
- Healthcheck en `/health` (o raíz para frontend)
- No exponer puertos al host — solo `expose` en el compose

## Si algo no funciona

1. Coolify → Logs del servicio (verbose)
2. Verificá que las env vars están seteadas (no basta con .env.example)
3. Avísame antes de tocar config de proxy, networks o firewall

## Deadline

Consigna 4.0: **2026-05-22**
