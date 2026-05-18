# Plan de Mailing — Resend Multi-Dominio (WebsHooks Platform)

> **Fecha:** 2026-05-17
> **Autor:** Federico Monfasani
> **Estado:** Guía de referencia + plan de implementación
> **Documentos relacionados:**
>
> - [`plan_fork_coolify_webshooks_platform.md`](./plan_fork_coolify_webshooks_platform.md) — visión del fork
> - [`plan_saneamiento.md`](./plan_saneamiento.md) — corto plazo
>
> **Alcance:** Stack unificado de email transaccional + casillas por usuario, sobre Resend, replicable a N dominios de proyectos. Esta guía es la base del módulo "Email Service" del fork de Coolify.

---

## 0. Filosofía

Un solo proveedor (**Resend**) sirve a **N marcas/dominios** con **M usuarios cada una**. La arquitectura es:

- **Saliente (transaccional + humano)**: Resend
- **Entrante (recibir mails)**: Cloudflare Email Routing (gratis)
- **Wrapper de aplicación**: una librería única que cada app importa
- **Provisioning**: automatizado vía Resend API (objetivo del fork)

**Regla**: cuando aparece un proyecto nuevo, agregar un dominio a Resend + configurar DNS + crear N usuarios debe tomar **menos de 10 minutos**.

---

## 1. Arquitectura objetivo

```
┌──────────────────────────────────────────────────────────────────┐
│                       RESEND (1 cuenta Pro)                      │
│  Dominios verificados:                                           │
│    webshooks.com   luzguffanti.com   anamurat.com   argfy.com    │
│                                                                  │
│  Cada dominio: ∞ users (no consume slot extra)                   │
│  API Keys: 1 por proyecto (scoped)                               │
└────────┬─────────────────────────────────────────────────────────┘
         │ SMTP / API
         │
┌────────▼─────────────────────────────────────────────────────────┐
│                      APPS (clientes Resend)                      │
│  Coolify panel    │   argfy SaaS    │   anamurat web             │
│  ws-zapateria     │   ws-tienda     │   luzguffanti site         │
│  ...                                                             │
│  Cada una usa su propia API key + sender                         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│              CLOUDFLARE EMAIL ROUTING (gratis)                   │
│  Por dominio:                                                    │
│    *@webshooks.com   → fmonfasani@gmail.com (catch-all)          │
│    mateo@webshooks   → mateollorente25@gmail.com                 │
│    luz@luzguffanti   → luz.guffanti.real@gmail.com               │
│    noreply@*         → drop                                      │
└──────────────────────────────────────────────────────────────────┘
```

**Resultado**:
- Cuando una app manda mail → sale por Resend con DKIM firmado del dominio correcto
- Cuando un usuario responde a `mateo@webshooks.com` → Cloudflare lo reenvía al Gmail personal de Mateo
- Mateo escribe **desde su Gmail real** pero puede configurarlo para que el `From` diga `mateo@webshooks.com` (Gmail "Send As")

---

## 2. Costo y modelo de cuentas

### Decisión: 1 sola cuenta Resend Pro ($20/mes) para todo

| Plan | Dominios | Mails/mes | Costo | Cuándo |
|------|----------|-----------|-------|--------|
| Free | 1 | 3.000 | $0 | Solo si tenés UN dominio |
| **Pro** | **10** | **50.000** | **$20/mes** | **Default desde el 2º dominio** |
| Scale | unlimited | 100k+ | $90+ | Cuando >50k mails/mes |

**Por qué NO multiple cuentas free** (1 por dominio):
- N dashboards, N API keys, N webhooks a mantener
- Imposible billing/reporting consolidado
- Aceptable solo si tenés ≤2 dominios y volumen muy bajo

**Por qué Pro desde el principio**: $20/mes para resolver TODO el mailing de TODOS los proyectos durante años. Cualquier hora-hombre que te ahorre la simplificación lo paga 100 veces.

---

## 3. Setup inicial (una sola vez)

### 3.1 Crear cuenta Resend

1. [resend.com/signup](https://resend.com/signup) con `fmonfasani@gmail.com`
2. Activar 2FA
3. Settings → Billing → Upgrade a **Pro** ($20/mes)

### 3.2 Generar API Key root

- Settings → API Keys → "Create API Key"
- Name: `master-admin`
- Permission: `Full access`
- **Guardar en password manager**, nunca commitear

### 3.3 Configurar webhooks (uno solo, para todo)

- Settings → Webhooks → "Add Endpoint"
- URL: `https://email-events.webshooks.com/resend` (lo deployamos después)
- Events: `email.sent`, `email.delivered`, `email.bounced`, `email.complained`, `email.opened`, `email.clicked`
- Guardar `Signing Secret`

---

## 4. Agregar un dominio nuevo a Resend (template repetible)

Esta es la operación que vas a hacer cada vez que onboardees un proyecto. **Objetivo: ≤10 min.**

### Paso A — Verificar dominio en Resend

1. Resend → Domains → "Add Domain" → `<tudominio>.com`
2. Resend te muestra 3-4 DNS records. Por ejemplo, para `webshooks.com`:

```
Tipo    Nombre                            Valor
MX      send.webshooks.com                feedback-smtp.us-east-1.amazonses.com (prio 10)
TXT     send.webshooks.com                "v=spf1 include:amazonses.com ~all"
CNAME   resend._domainkey.webshooks.com   resend.domainkey.u-xxxx.amazonses.com
TXT     _dmarc.webshooks.com              "v=DMARC1; p=none; rua=mailto:dmarc@webshooks.com"
```

3. **Pegar en Cloudflare DNS** (zona del dominio) → guardar cada record exactamente como lo da Resend
4. Volver a Resend → "Verify DNS" → esperar 1-5 min → estado `Verified` ✓

### Paso B — Generar API Key scoped por proyecto

- Resend → API Keys → "Create"
- Name: `<proyecto>` (e.g. `webshooks-coolify`, `argfy`, `luzguffanti-site`)
- Permission: `Sending access` (no admin)
- Domain: restringir al dominio recién verificado
- Guardar key → setearla en Coolify env vars como `RESEND_API_KEY` del proyecto

### Paso C — Configurar Cloudflare Email Routing (recepción)

1. Cloudflare → tu dominio → **Email** → "Get started"
2. Cloudflare agrega 3 MX records automáticamente
3. **Pero hay un conflicto**: Resend ya usa `send.webshooks.com` como MX. La solución es que Cloudflare Routing maneja `webshooks.com` (raíz) y Resend maneja `send.webshooks.com` (subdominio). NO chocan.
4. Crear rutas:

| Match | Action |
|-------|--------|
| `*@webshooks.com` (catch-all) | Forward to `fmonfasani@gmail.com` |
| `mateo@webshooks.com` | Forward to `mateollorente25@gmail.com` |
| `valentino@webshooks.com` | Forward to `valentinopicco2004@gmail.com` |
| `aldana@webshooks.com` | Forward to `oviedoaldana16@gmail.com` |
| `joaquin@webshooks.com` | Forward to `joaquinlevis2004@gmail.com` |
| `noreply@webshooks.com` | Drop |
| `dmarc@webshooks.com` | Forward to `fmonfasani@gmail.com` (informes DMARC) |

### Paso D — (Opcional) "Send As" en Gmail para cada usuario

Esto permite que el usuario **responda desde su Gmail real pero el `From` diga su dirección de marca**:

1. Cada usuario va a su Gmail → Settings → Accounts → "Send mail as" → "Add another email address"
2. Email: `mateo@webshooks.com`, Name: `Mateo Llorente`
3. Treat as alias: ✓
4. Cuando le pida SMTP: usar el de Resend SMTP (`smtp.resend.com:587`, usuario `resend`, password = la API key del proyecto)
5. Confirmar con el link que llega al inbox (vía Cloudflare Routing)

A partir de ahí, Mateo escribe mails desde Gmail Web/App y el receptor ve `Mateo Llorente <mateo@webshooks.com>`.

**Trade-off**: cada usuario necesita coordinarse para el setup. Si son colaboradores que no van a responder mails con frecuencia, podés saltarte este paso y solo dejar el reenvío (Paso C).

---

## 5. Ejemplos concretos por dominio

### 5.1 webshooks.com (panel + colaboradores)

**Senders salientes** (todos vía Resend, dominio `webshooks.com`):

| Sender | Uso | API Key |
|--------|-----|---------|
| `coolify@webshooks.com` | Invitaciones Coolify, deploys notifications | `webshooks-coolify` |
| `mateo@webshooks.com` | Mateo manda mails desde su app + Gmail Send As | `webshooks-coolify` (compartida) |
| `valentino@webshooks.com` | Idem | mismo |
| `aldana@webshooks.com` | Idem | mismo |
| `joaquin@webshooks.com` | Idem | mismo |
| `noreply@webshooks.com` | Transactional genérico | mismo |
| `info@webshooks.com` | Contacto público | mismo (vía Send As tuya) |

**Rutas entrantes** (Cloudflare):

```
mateo@      → mateollorente25@gmail.com
valentino@  → valentinopicco2004@gmail.com
aldana@     → oviedoaldana16@gmail.com
joaquin@    → joaquinlevis2004@gmail.com
info@       → fmonfasani@gmail.com
*@          → fmonfasani@gmail.com  (catch-all)
noreply@    → drop
```

### 5.2 luzguffanti.com

**Senders salientes**:

| Sender | Uso |
|--------|-----|
| `admin@luzguffanti.com` | Federico/owner del proyecto |
| `info@luzguffanti.com` | Contacto público |
| `member1@luzguffanti.com` | Colaborador 1 |
| `luz@luzguffanti.com` | Luz Guffanti (cliente/dueña) |
| `noreply@luzguffanti.com` | Transactional |

**Rutas entrantes** (Cloudflare):

```
admin@       → fmonfasani@gmail.com
info@        → luz.guffanti@gmail.com  (ella ve consultas)
member1@     → colaborador1@gmail.com
luz@         → luz.guffanti@gmail.com
*@           → fmonfasani@gmail.com  (catch-all)
noreply@     → drop
```

**Send As recomendado**: Luz configura `luz@luzguffanti.com` como alias en su Gmail real → escribe mails con su marca pero usando su Gmail.

### 5.3 anamurat.com

Mismo patrón. Definí los usuarios cuando arranque ese proyecto:

```
admin@anamurat.com         → fmonfasani@gmail.com
ana@anamurat.com           → ana.murat@gmail.com  (cliente)
info@anamurat.com          → ana.murat@gmail.com
noreply@anamurat.com       → drop
*@anamurat.com             → fmonfasani@gmail.com  (catch-all)
```

### 5.4 argfy.com

Más fuerte en transaccional (SaaS):

| Sender | Uso |
|--------|-----|
| `noreply@argfy.com` | Signup, password reset, payment receipts |
| `support@argfy.com` | Customer support outbound |
| `team@argfy.com` | Comunicaciones del equipo |
| `billing@argfy.com` | Facturas + cobros |

**Rutas entrantes**:

```
support@   → fmonfasani@gmail.com  (después: tabla zendesk-lite)
team@      → fmonfasani@gmail.com
billing@   → fmonfasani@gmail.com
*@         → fmonfasani@gmail.com  (catch-all)
noreply@   → drop
```

### 5.5 Template universal para cualquier proyecto nuevo

```
Dominio: <proyecto>.com

Senders (Resend):
  noreply@<proyecto>.com    — transaccional sistema
  admin@<proyecto>.com      — owner/Federico
  info@<proyecto>.com       — contacto público
  {cliente}@<proyecto>.com  — cliente principal (Luz, Ana, etc.)
  {member}@<proyecto>.com   — colaboradores

Rutas entrantes (Cloudflare):
  *@           → catch-all hacia fmonfasani@gmail.com
  noreply@     → drop
  {cliente}@   → gmail real del cliente
  {member}@    → gmail real del colaborador
  dmarc@       → fmonfasani@gmail.com (para informes DMARC)

DNS Resend (4 records):
  MX     send.<proyecto>.com         feedback-smtp.us-east-1.amazonses.com
  TXT    send.<proyecto>.com         "v=spf1 include:amazonses.com ~all"
  CNAME  resend._domainkey.<proyecto>.com   <provista por Resend>
  TXT    _dmarc.<proyecto>.com       "v=DMARC1; p=none; rua=mailto:dmarc@<proyecto>.com"
```

---

## 6. Integración en las apps

### 6.1 Variables de entorno por proyecto

Cada app tiene en Coolify estos env vars:

```bash
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxx     # encrypted
EMAIL_FROM_ADDRESS=noreply@webshooks.com
EMAIL_FROM_NAME=WebsHooks
EMAIL_REPLY_TO=info@webshooks.com          # opcional
EMAIL_WEBHOOK_SECRET=whsec_xxxxxxxxxx      # para verificar webhooks Resend
```

### 6.2 Wrapper unificado (Python — para argfy y FastAPI apps)

```python
# common/services/mailer.py
import os
import resend
from typing import Optional
from pydantic import BaseModel

class EmailPayload(BaseModel):
    to: str | list[str]
    subject: str
    html: Optional[str] = None
    text: Optional[str] = None
    template_id: Optional[str] = None
    template_vars: Optional[dict] = None
    tags: Optional[list[dict]] = None
    reply_to: Optional[str] = None

class Mailer:
    def __init__(self):
        resend.api_key = os.environ["RESEND_API_KEY"]
        self.from_address = os.environ["EMAIL_FROM_ADDRESS"]
        self.from_name = os.environ.get("EMAIL_FROM_NAME", "")
        self.default_reply_to = os.environ.get("EMAIL_REPLY_TO")

    def send(self, payload: EmailPayload) -> str:
        params = {
            "from": f'{self.from_name} <{self.from_address}>',
            "to": [payload.to] if isinstance(payload.to, str) else payload.to,
            "subject": payload.subject,
            "reply_to": payload.reply_to or self.default_reply_to,
            "tags": payload.tags or [],
        }
        if payload.html:
            params["html"] = payload.html
        if payload.text:
            params["text"] = payload.text
        result = resend.Emails.send(params)
        return result["id"]
```

Uso:

```python
mailer = Mailer()
mailer.send(EmailPayload(
    to="mateollorente25@gmail.com",
    subject="Invitación a Coolify",
    html=render("coolify_invite.html", {"name": "Mateo", "link": "..."}),
    tags=[{"name": "category", "value": "invitation"}],
))
```

### 6.3 Wrapper para Node/Next.js (apps de colaboradores)

```typescript
// lib/mailer.ts
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY!);

export async function sendEmail(opts: {
  to: string | string[];
  subject: string;
  html?: string;
  text?: string;
  tags?: { name: string; value: string }[];
  replyTo?: string;
}) {
  return resend.emails.send({
    from: `${process.env.EMAIL_FROM_NAME} <${process.env.EMAIL_FROM_ADDRESS}>`,
    to: Array.isArray(opts.to) ? opts.to : [opts.to],
    subject: opts.subject,
    html: opts.html,
    text: opts.text,
    tags: opts.tags ?? [],
    replyTo: opts.replyTo ?? process.env.EMAIL_REPLY_TO,
  });
}
```

### 6.4 Templates HTML compartidos

Crear repo `webshooks-org/email-templates` con templates Mustache/Handlebars + MJML:

```
email-templates/
├── invitation.mjml
├── password-reset.mjml
├── deploy-success.mjml
├── deploy-failure.mjml
├── welcome.mjml
└── shared/
    ├── header.mjml
    └── footer.mjml
```

Cada app importa el package como dependencia y le pasa `brand` por contexto:

```python
html = render_email("invitation", {
    "brand_name": "WebsHooks",
    "brand_color": "#0066CC",
    "user_name": "Mateo",
    "invite_link": "https://coolify.webshooks.com/invite/xyz"
})
```

---

## 7. Recepción de webhooks Resend (centralized)

Un solo endpoint que recibe TODOS los eventos de Resend, los guarda en una DB compartida, y dispara acciones por proyecto.

### 7.1 Tabla `email_events`

```sql
CREATE TABLE email_events (
  id              UUID PRIMARY KEY,
  event_type      TEXT NOT NULL,   -- sent|delivered|bounced|complained|opened|clicked
  email_id        TEXT NOT NULL,   -- ID de Resend
  to_address      TEXT NOT NULL,
  from_address    TEXT NOT NULL,
  from_domain     TEXT NOT NULL,   -- particionado por dominio
  project_tag     TEXT,            -- de los tags del send
  subject         TEXT,
  payload_json    JSONB,
  occurred_at     TIMESTAMPTZ NOT NULL,
  received_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_domain_date ON email_events(from_domain, occurred_at DESC);
CREATE INDEX idx_events_project ON email_events(project_tag, event_type);
```

### 7.2 Endpoint `https://email-events.webshooks.com/resend`

```python
@app.post("/resend")
async def resend_webhook(request: Request):
    # Verificar firma HMAC
    signature = request.headers.get("svix-signature")
    body = await request.body()
    verify_signature(body, signature, os.environ["RESEND_WEBHOOK_SECRET"])

    payload = await request.json()
    event_type = payload["type"]
    data = payload["data"]

    EmailEvent.create(
        event_type=event_type,
        email_id=data["email_id"],
        to_address=data["to"][0],
        from_address=data["from"],
        from_domain=data["from"].split("@")[1],
        project_tag=next((t["value"] for t in data.get("tags", []) if t["name"]=="project"), None),
        subject=data.get("subject"),
        payload_json=data,
        occurred_at=parse_ts(data["created_at"]),
    )

    # Disparar acciones por evento
    if event_type == "email.bounced":
        notify_owner(data)
    return {"ok": True}
```

### 7.3 Dashboard simple

`https://email-events.webshooks.com/dashboard` muestra por dominio:

- Mails enviados últimos 7/30 días
- % delivery / bounce / complaint
- Top destinos con bounces (limpiar lista)
- Volumen por hora (detectar abuso)

Servicio mínimo: FastAPI + HTMX. Lo deployamos en Coolify como un proyecto más.

---

## 8. Provisioning automatizado (objetivo para el fork de Coolify)

Hoy: agregar un dominio toma 10 min manual.
**Objetivo del fork**: 1 click.

### 8.1 Módulo "Email Service" en Coolify-fork

UI en Project Settings:

```
┌──────────────────────────────────────────────────────────┐
│  Email Service                                           │
│  ─────────────────────────────────────────────────────   │
│  Domain: [ luzguffanti.com               ]               │
│                                                          │
│  Provider: ◉ Resend  ○ SES  ○ Postmark                   │
│  API key: [encrypted, set in env]                        │
│                                                          │
│  Senders:                                                │
│    ✓ noreply@luzguffanti.com  (transactional)            │
│    ✓ admin@luzguffanti.com    → fede@gmail              │
│    ✓ info@luzguffanti.com     → luz.guffanti@gmail      │
│    ✓ luz@luzguffanti.com      → luz.guffanti@gmail      │
│    [ + Add sender ]                                      │
│                                                          │
│  DNS records (auto-generated):                           │
│    [ Copy to clipboard ] [ Apply via Cloudflare API ]    │
│                                                          │
│  Status: ⚠ DNS not verified yet                          │
│  [ Verify ] [ Send test email ]                          │
└──────────────────────────────────────────────────────────┘
```

### 8.2 Flujo automatizado

1. User clickea "Enable Email" en un proyecto
2. Coolify-fork llama `POST /v1/domains` a Resend API → guarda el DKIM/SPF/DMARC
3. Si el user conectó Cloudflare account → Coolify aplica los DNS records vía Cloudflare API
4. Coolify-fork llama `POST /v1/api-keys` con scope a ese dominio → guarda la key encrypted
5. Setea env vars en el servicio: `RESEND_API_KEY`, `EMAIL_FROM_ADDRESS`, etc.
6. Mostrar "Send test email" → llamar `resend.emails.send()` con un template fixed
7. Si llega ✓ → marcar como "active"

### 8.3 Schema de DB del fork (tabla nueva)

```sql
CREATE TABLE webshooks_email_services (
  id                BIGSERIAL PRIMARY KEY,
  project_id        BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  provider          TEXT NOT NULL DEFAULT 'resend',  -- resend|ses|postmark
  domain            TEXT NOT NULL,
  resend_domain_id  TEXT,
  api_key_encrypted TEXT NOT NULL,
  webhook_secret    TEXT,
  status            TEXT NOT NULL DEFAULT 'pending', -- pending|verified|failed
  dns_records       JSONB,
  senders           JSONB,                            -- array de {address, forward_to, gmail_send_as}
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  verified_at       TIMESTAMPTZ
);
```

### 8.4 Endpoints REST del fork

```
POST   /api/v1/projects/{id}/email          # crear email service
GET    /api/v1/projects/{id}/email          # estado actual
POST   /api/v1/projects/{id}/email/verify   # re-check DNS
POST   /api/v1/projects/{id}/email/senders  # agregar sender
POST   /api/v1/projects/{id}/email/test     # send test email
DELETE /api/v1/projects/{id}/email          # desactivar
```

### 8.5 Integración con Cloudflare (opcional pero killer)

Si el user conecta Cloudflare API Token con permisos `Zone.DNS.Edit + Zone.Email Routing.Edit`:

- Coolify-fork aplica los 4 DNS records automáticamente
- Configura las rutas de Email Routing automáticamente
- Verifica el dominio en Resend (call automático)
- Tiempo total: **~30 segundos en lugar de 10 minutos manuales**

Implementación: usar Cloudflare API v4 SDK.

---

## 9. Roadmap de implementación

### Fase 1 — Manual (esta semana)

- [ ] Crear cuenta Resend con `fmonfasani@gmail.com`
- [ ] Upgrade a Pro ($20/mes)
- [ ] Agregar dominio `webshooks.com` → DNS en Cloudflare → verificar
- [ ] API key `webshooks-coolify` → setear en Coolify
- [ ] Cambiar Coolify SMTP a Resend (`smtp.resend.com:465`, user `resend`, password = API key)
- [ ] Test email a `fmonfasani@gmail.com`
- [ ] **Mandar Ola 1 de invitaciones SCRUM** (el unblock real)
- [ ] Configurar Cloudflare Email Routing para `webshooks.com`:
  - `mateo@`, `valentino@`, `aldana@`, `joaquin@`, `info@`, catch-all
- [ ] (Opcional) `fede@webshooks.com` con Gmail Send As

### Fase 2 — Replicar a los otros dominios (próximas 2 semanas)

- [ ] `argfy.com` en Resend + Cloudflare Routing
- [ ] `luzguffanti.com` cuando arranque proyecto
- [ ] `anamurat.com` cuando arranque proyecto
- [ ] Wrapper `Mailer` en argfy backend (`backend/app/services/mailer.py`)
- [ ] Webhook receiver `email-events.webshooks.com` deployado en Coolify

### Fase 3 — Templates compartidos (mes 2)

- [ ] Repo `webshooks-org/email-templates` con MJML + Handlebars
- [ ] CI que compila MJML → HTML
- [ ] Publicar como package npm + PyPI
- [ ] Migrar inline templates de las apps a este package
- [ ] Dashboard básico `email-events.webshooks.com/dashboard`

### Fase 4 — Provisioning automatizado en el fork (mes 3-4)

- [ ] Schema `webshooks_email_services` en migración
- [ ] UI "Email Service" en Coolify-fork
- [ ] Integración Resend API (crear dominios + API keys)
- [ ] Integración Cloudflare API (aplicar DNS + Routing)
- [ ] Endpoints REST del módulo
- [ ] Test email flow end-to-end
- [ ] Feature flag `webshooks.feature.email_service`

### Fase 5 — Multi-provider (mes 6+)

- [ ] Soporte SES como alternativa (cuando volumen lo justifique)
- [ ] Soporte Postmark (premium deliverability)
- [ ] Auto-switching por reputación (si Resend bouncea mucho un dominio → fallback SES)

---

## 10. Seguridad y compliance

- **Nunca** commitear API keys ni en `.env` del repo
- API keys siempre **encrypted en Coolify** (marcar `Is Secret`)
- DMARC empezar en `p=none` (solo reporta), pasar a `p=quarantine` cuando estabilice, eventualmente `p=reject`
- Reportes DMARC mandados a `dmarc@<dominio>` y forwarded a tu inbox (revisar mensual)
- Webhook signing secret en encrypted env var
- Audit log: cada `email.bounced` o `email.complained` queda registrado para compliance
- **GDPR/LGPD**: tabla `email_unsubscribes` y respetar opt-outs siempre

---

## 11. Métricas de éxito

| Métrica | Hoy | Fase 2 | Fase 4 (fork ready) |
|---------|-----|--------|---------------------|
| Tiempo de onboarding dominio nuevo | N/A | 10 min manual | 30 seg automático |
| Deliverability rate | N/A | >98% | >99% |
| Bounce rate | N/A | <2% | <1% |
| Complaint rate | N/A | <0.1% | <0.05% |
| Costo por 1k mails | N/A | $0.40 | $0.40 (Resend) o $0.10 (SES) |
| Templates compartidos | 0 | 5 | 15+ |
| Dominios soportados simultáneos | 1 (Gmail) | 4 | unlimited |

---

## 12. Decisiones abiertas

- [ ] ¿Federico paga el Resend Pro de su bolsillo o se factura entre proyectos? Sugerencia: argfy lo absorbe (es el mayor consumidor proyectado)
- [ ] ¿Los colaboradores tienen acceso a su propia API key o todo va por la master? Sugerencia: hasta tener el fork, la master. Después, API key scoped por proyecto en el módulo Email Service
- [ ] ¿Implementamos Gmail "Send As" como tarea obligatoria de onboarding o opcional? Sugerencia: opcional, lo decide cada colaborador
- [ ] ¿Catch-all forward a Gmail personal de Federico es OK o conviene una casilla compartida (`team@webshooks.com` en Workspace)? Sugerencia: Workspace cuando el volumen lo justifique (>50 mails/día llegando)

---

## Apéndice A — Cheatsheet de records DNS (templates)

### A.1 Records Resend (por dominio, en Cloudflare)

```
MX     send.<dom>      feedback-smtp.us-east-1.amazonses.com   10
TXT    send.<dom>      "v=spf1 include:amazonses.com ~all"
CNAME  resend._domainkey.<dom>   <provista por Resend, varía>
TXT    _dmarc.<dom>    "v=DMARC1; p=none; rua=mailto:dmarc@<dom>; pct=100"
```

### A.2 Records Cloudflare Email Routing (auto-creados al activar)

```
MX     <dom>           route1.mx.cloudflare.net   13
MX     <dom>           route2.mx.cloudflare.net   38
MX     <dom>           route3.mx.cloudflare.net   46
TXT    <dom>           "v=spf1 include:_spf.mx.cloudflare.net ~all"
```

⚠️ **Atención al SPF**: si tenés ambos (Resend para enviar + Cloudflare Routing para recibir), el record SPF de Cloudflare aplica a `<dom>` raíz, pero los mails de Resend salen como `<user>@send.<dom>` (subdomain) que tiene su propio SPF. **No chocan**.

Si querés que `<user>@<dom>` (raíz) también pase SPF cuando lo manda Resend, el record TXT raíz debería ser:

```
TXT    <dom>    "v=spf1 include:_spf.mx.cloudflare.net include:amazonses.com ~all"
```

---

## Apéndice B — Comparación de providers (referencia)

| Provider | Free | Pro/mes | Costo/1k mails (paid) | Deliverability | DX |
|----------|------|---------|----------------------|----------------|-----|
| **Resend** | 100/d, 3k/mo, 1 dom | $20 (10 dom, 50k) | $0.40 | ★★★★ | ★★★★★ |
| Postmark | 100/mo trial | $15 (10k) | $1.50 | ★★★★★ | ★★★★ |
| Mailgun | 5k/mo (3 meses) | $35 (50k) | $0.80 | ★★★★ | ★★★ |
| Amazon SES | 200/d desde EC2 | $0.10/1k | $0.10 | ★★★★ | ★★ (crudo) |
| Brevo | 300/d | $25 (20k) | $1.25 | ★★★ | ★★★ |
| SendGrid | 100/d | $20 (50k) | $0.40 | ★★★ | ★★★ |
| Self-hosted (Postal) | — | $5 VPS + SES relay | $0.10 | ★★★ (depende relay) | ★ |

**Veredicto**: Resend Pro es el sweet spot para WebsHooks. SES queda como fallback de costo a escala.

---

> **Próximo paso real**: crear la cuenta Resend, verificar `webshooks.com`, configurar SMTP en Coolify y mandar Ola 1 — todo descripto en §9 Fase 1.
