# Secrets para argfy en Coolify UI

Setear cada variable en Coolify → argfy → cada servicio → Environment Variables.
Marcar como **encrypted** las que contienen credenciales.

## Backend (argfy-api)

| Variable | Origen | Encrypted |
|----------|--------|-----------|
| `POSTGRES_DB` | Definir (ej: argfy) | no |
| `POSTGRES_USER` | Definir (ej: argfy) | no |
| `POSTGRES_PASSWORD` | Generar (pwgen 64) | sí |
| `SECRET_KEY` | Generar (openssl rand -hex 32) | sí |
| `JWT_SECRET` | Generar (openssl rand -hex 32) | sí |
| `MP_ACCESS_TOKEN` | Mercado Pago → Credenciales → Access Token | sí |
| `MP_WEBHOOK_SECRET` | Mercado Pago → Webhooks → Secret | sí |
| `GOOGLE_CLIENT_ID` | Google Cloud Console → OAuth 2.0 | no |
| `GOOGLE_CLIENT_SECRET` | Google Cloud Console → OAuth 2.0 | sí |
| `SENTRY_DSN` | Sentry → argfy project → DSN | no |
| `CORS_ORIGINS` | `["https://argfy.com","https://www.argfy.com"]` | no |

## Frontend (argfy-web)

| Variable | Valor |
|----------|-------|
| `NEXT_PUBLIC_API_BASE` | `https://api.argfy.com/api/v1` |
| `NEXT_PUBLIC_BACKEND_URL` | `https://api.argfy.com` |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | misma que GOOGLE_CLIENT_ID del backend |

## GitHub Actions (repo argfy)

| Secret | Valor |
|--------|-------|
| `COOLIFY_WEBHOOK_URL` | Coolify → argfy → Webhooks → copiar URL |
| `COOLIFY_WEBHOOK_TOKEN` | Coolify → argfy → Webhooks → copiar token |
