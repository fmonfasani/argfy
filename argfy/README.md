# argfy# 🚀 Argfy Platform - Demo v0.1

Plataforma de datos económicos argentinos en tiempo real. Proximamente!

## 📋 Descripción

Argfy es una plataforma completa que proporciona:
- **Indicadores económicos argentinos** en tiempo real
- **Datos históricos** con visualizaciones interactivas  
- **Noticias financieras** categorizadas
- **API REST** documentada para desarrolladores
- **Dashboard interactivo** con gráficos

## 🏗️ Arquitectura

```
argfy-platform/
├── frontend/          # Next.js 14 + TypeScript + Tailwind
├── backend/           # FastAPI + SQLAlchemy + SQLite
├── data-pipelines/    # Scripts de obtención de datos
├── docs/              # Documentación
└── deployment/        # Configuraciones de deploy
```

## 🛠️ Stack Tecnológico

### Frontend
- **Next.js 14** con App Router
- **TypeScript** para type safety
- **Tailwind CSS** para estilos
- **Recharts** para visualizaciones
- **Heroicons** para iconografía

### Backend
- **FastAPI** framework moderno de Python
- **SQLAlchemy** ORM para base de datos
- **SQLite** base de datos (migración futura a PostgreSQL)
- **Uvicorn** servidor ASGI
- **Pandas** para procesamiento de datos

### Integración
- **BCRA API** para datos oficiales
- **TradingView** widgets para mercados
- **CORS** configurado para desarrollo

## ⚡ Instalación Rápida

### 1. Clonar y Setup Inicial

```bash
# Clonar el repositorio
git clone <tu-repo-url>
cd argfy-platform

# Crear estructura de directorios
mkdir frontend backend data-pipelines docs deployment
```

### 2. Setup Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate

# Instalar dependencias
pip install fastapi[all] uvicorn sqlalchemy pandas requests python-multipart python-dotenv

# Guardar dependencias
pip freeze > requirements.txt

# Inicializar base de datos con datos demo
python scripts/init_database.py
```

### 3. Setup Frontend

```bash
cd ../frontend

# Crear proyecto Next.js
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir

# Instalar dependencias adicionales
npm install recharts lucide-react @headlessui/react @heroicons/react

# Crear archivos de configuración
```

### 4. Configuración de Entorno

Crear archivo `.env.local` en el frontend:
```bash
# frontend/.env.local
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
```

Crear archivo `.env` en el backend:
```bash
# backend/.env
DATABASE_URL=sqlite:///./data/argentina.db
ENVIRONMENT=development
```

## 🚀 Ejecutar el Proyecto

### Iniciar Backend

```bash
cd backend
source venv/bin/activate  # Activar entorno virtual
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en:
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Iniciar Frontend

```bash
cd frontend
npm run dev
```

El frontend estará disponible en:
- **Aplicación**: http://localhost:3000

## 📊 Funcionalidades Implementadas

### ✅ Backend API

- **GET** `/api/v1/indicators/current` - Indicadores actuales
- **GET** `/api/v1/indicators/historical/{type}` - Datos históricos
- **GET** `/api/v1/indicators/news` - Noticias económicas
- **GET** `/api/v1/indicators/summary` - Resumen del dashboard
- **POST** `/api/v1/indicators/refresh` - Actualizar datos

### ✅ Frontend

- **Landing Page** responsive con datos en tiempo real
- **Dashboard Modal** con gráficos interactivos
- **Navegación** completa y búsqueda
- **TradingView Integration** para datos de mercado
- **Responsive Design** mobile-first

### ✅ Datos Incluidos

- **Dólar Blue, Oficial, MEP** - Cotizaciones
- **Inflación** - INDEC
- **Reservas BCRA** - Banco Central
- **Riesgo País** - JP Morgan
- **Merval** - Bolsa de valores
- **Noticias** - Categorizadas por sector

## 🔧 Scripts Útiles

### Backend

```bash
# Inicializar base de datos
python scripts/init_database.py

# Agregar más datos históricos
python scripts/init_database.py --extend

# Ejecutar tests
pytest

# Linting
flake8 app/
```

### Frontend

```bash
# Desarrollo
npm run dev

# Build para producción
npm run build

# Linting
npm run lint

# Type checking
npm run type-check
```

## 📱 Uso de la Aplicación

### 1. Página Principal
- Navega por las **6 categorías** de datos económicos
- Cada tarjeta muestra indicadores clave en tiempo real
- Click en **"Ver Dashboard"** para análisis detallado

### 2. Dashboard Interactivo
- **4 indicadores principales** en tiempo real
- **Gráficos históricos** de 30 días
- **Tabla completa** de todos los indicadores
- Selector de diferentes tipos de gráficos

### 3. Navegación
- **Búsqueda** funcional en el header
- **Menú móvil** responsive
- **Navegación secundaria** por categorías

## 🌐 API Documentation

### Endpoints Principales

#### Obtener Indicadores Actuales
```bash
curl -X GET "http://localhost:8000/api/v1/indicators/current"
```

#### Obtener Datos Históricos
```bash
curl -X GET "http://localhost:8000/api/v1/indicators/historical/dolar_blue?days=30"
```

#### Obtener Noticias
```bash
curl -X GET "http://localhost:8000/api/v1/indicators/news?limit=6"
```

### Respuesta Ejemplo

```json
{
  "data": [
    {
      "id": 1,
      "indicator_type": "dolar_blue",
      "value": 1047.0,
      "date": "2024-06-25T10:00:00",
      "source": "demo",
      "is_active": true
    }
  ],
  "timestamp": "2024-06-25T10:00:00",
  "count": 1,
  "status": "success"
}
```

## 🚀 Deploy

### Backend (Render)

1. Crear archivo `render.yaml`:
```yaml
services:
  - type: web
    name: argfy-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

2. Conectar repositorio con Render
3. Deploy automático en cada push

### Frontend (Vercel)

1. Crear archivo `vercel.json`:
```json
{
  "name": "argfy-frontend",
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "env": {
    "NEXT_PUBLIC_BACKEND_URL": "https://api.argfy.com"
  }
}
```

2. Conectar repositorio con Vercel
3. Deploy automático

## 🔄 Desarrollo Continuo

### Próximas Funcionalidades

1. **Semana 5-6**: Autenticación y API Keys
2. **Mes 2**: Más fuentes de datos (Bloomberg, Yahoo Finance)
3. **Mes 3**: Dashboard personalizable
4. **Mes 4**: Modelo de suscripción

### Mejoras Técnicas

- [ ] Cache con Redis
- [ ] Tests automatizados
- [ ] CI/CD con GitHub Actions
- [ ] Monitoreo con Sentry
- [ ] Base de datos PostgreSQL

## 🐛 Troubleshooting

### Errores Comunes

#### Backend no inicia
```bash
# Verificar que el entorno virtual está activado
source venv/bin/activate

# Verificar dependencias
pip install -r requirements.txt

# Verificar puerto disponible
lsof -i :8000
```

#### Frontend no conecta con Backend
```bash
# Verificar variables de entorno
cat frontend/.env.local

# Verificar CORS en backend
curl -X OPTIONS http://localhost:8000/api/v1/indicators/current
```

#### Base de datos vacía
```bash
# Reinicializar base de datos
python scripts/init_database.py
```

## 📞 Soporte

- **GitHub Issues**: Para reportar bugs
- **Email**: contact@argfy.com
- **Documentación**: `/docs` en el backend

## 📄 Licencia

MIT License - ver archivo LICENSE para detalles

---

**Desarrollado con ❤️ para la comunidad financiera argentina**

*Demo v0.1 - Datos actualizados en tiempo real*
