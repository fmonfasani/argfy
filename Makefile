.PHONY: install dev build lint vercel-login vercel-deploy

PNPM := pnpm   # cámbialo por npm o yarn si usas otro gestor

install:                   ## Instala dependencias Node
	$(PNPM) install

dev:                       ## Dev server local
	$(PNPM) dev

build:                     ## Build de producción local
	$(PNPM) build

lint:                      ## ESLint + Type Check
	$(PNPM) lint && $(PNPM) type-check

# --- Tareas Vercel CLI ------------------
# Requiere: npm i -g vercel

vercel-login:              ## Inicia sesión en Vercel
	vercel login

vercel-deploy: build       ## Sube a Vercel (prod)
	vercel --prod --confirm