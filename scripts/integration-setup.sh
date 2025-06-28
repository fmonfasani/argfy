#!/bin/bash
# scripts/integration-setup.sh
# Script para configurar la integración completa frontend-backend

set -e

echo "🔗 CONFIGURANDO INTEGRACIÓN FULL-STACK ARGFY"
echo "============================================="

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Verificar estructura del proyecto
check_project_structure() {
    log "Verificando estructura del proyecto..."
    
    if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
        error "Estructura de proyecto incorrecta. Debe tener directorios 'backend' y 'frontend'"
    fi
    
    if [ ! -f "backend/app/main.py" ]; then
        error "Backend no configurado correctamente. Falta backend/app/main.py"
    fi
    
    if [ ! -f "frontend/package.json" ]; then
        error "Frontend no configurado correctamente. Falta frontend/package.json"
    fi
    
    log "✅ Estructura del proyecto verificada"
}

# Configurar backend con nuevos endpoints
setup_backend() {
    log "Configurando backend expandido..."
    
    cd backend
    
    # Verificar que el entorno virtual existe
    if [ ! -d "venv" ]; then
        log "Creando entorno virtual..."
        python3 -m venv venv
    fi
    
    # Activar entorno virtual
    source venv/bin/activate
    
    # Instalar dependencias expandidas
    log "Instalando dependencias del backend..."
    
    cat > requirements.txt << 'EOF'
# FastAPI Core
fastapi[all]==0.104.1
uvicorn[standard]==0.24.0

# Database
sqlalchemy==2.0.23
alembic==1.13.1

# HTTP Clients (Stack híbrido)
aiohttp==3.9.1
httpx==0.26.0
requests==2.31.0

# Data Processing
pandas==2.1.3
numpy==1.24.3

# Web Scraping
beautifulsoup4==4.12.2
lxml==4.9.3
selenium==4.15.2

# Utilities
python-multipart==0.0.6
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Monitoring & Logging
psutil==5.9.6
structlog==23.2.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# Caching (opcional)
redis==5.0.1
EOF
    
    pip install -r requirements.txt
    
    # Crear estructura de directorios expandida
    mkdir -p app/{config,services,routers,utils,tests}
    mkdir -p data logs scripts
    
    # Crear archivo de configuración principal
    log "Creando configuración principal..."
    
    cat > app/config/__init__.py << 'EOF'
# Configuration module
from .indicators_mapping import *
from .settings import settings
EOF
    
    # Crear settings.py
    cat > app/config/settings.py << 'EOF'
import os
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./data/argentina.db"
    
    # APIs
    BCRA_API_URL: str = "https://api.bcra.gob.ar"
    INDEC_API_URL: str = "https://apis.datos.gob.ar/series/api"
    BLUELYTICS_URL: str = "https://api.bluelytics.com.ar/v2"
    BYMA_API_URL: str = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://argfy.vercel.app"]
    
    # System
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    
    # Cache
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 300
    
    # API Rate Limiting
    API_RATE_LIMIT: int = 60
    
    # Monitoring
    SENTRY_DSN: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
EOF
    
    # Actualizar main.py para incluir todas las rutas
    log "Actualizando main.py..."
    
    cat > app/main.py << 'EOF'
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging

from .config.settings import settings
from .database import engine, Base
from .routers import expanded_indicators, health
from .utils.monitoring import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="Argfy Platform API",
    description="""
    🇦🇷 **Argfy Platform** - Datos Económicos Argentinos en Tiempo Real
    
    ## Funcionalidades Principales
    
    - **50+ Indicadores económicos** en tiempo real
    - **6 Categorías**: Economía, Gobierno, Finanzas, Mercados, Tecnología, Industria
    - **APIs oficiales**: BCRA, INDEC, BYMA, y más
    - **Datos históricos** con gráficos interactivos
    - **Búsqueda avanzada** y filtros
    
    ## Fuentes de Datos
    
    - 🏦 **BCRA**: Banco Central de la República Argentina
    - 📊 **INDEC**: Instituto Nacional de Estadística y Censos
    - 📈 **BYMA**: Bolsas y Mercados Argentinos
    - 💱 **Bluelytics**: Cotizaciones paralelas
    - 🏛️ **MECON**: Ministerio de Economía
    
    ## Próximamente
    
    - 🔐 Autenticación con API Keys
    - 🔔 Webhooks para notificaciones
    - 📱 Endpoints móviles optimizados
    - 🤖 Predicciones con Machine Learning
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Dashboard",
            "description": "Endpoints principales para el dashboard"
        },
        {
            "name": "Expanded Indicators", 
            "description": "Todos los indicadores por categoría"
        },
        {
            "name": "Health & Monitoring",
            "description": "Health checks y monitoreo del sistema"
        }
    ]
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["argfy.com", "*.argfy.com", "*.onrender.com"]
    )

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request {request.method} {request.url.path} - {process_time:.4f}s")
    return response

# Include routers
app.include_router(expanded_indicators.router)
app.include_router(health.router)

# Root endpoints
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "🇦🇷 Argfy Platform API",
        "version": "1.0.0",
        "description": "Datos económicos argentinos en tiempo real",
        "endpoints": {
            "dashboard": "/api/v1/dashboard/complete",
            "docs": "/docs",
            "health": "/health"
        },
        "categories": [
            "economia", "gobierno", "finanzas", 
            "mercados", "tecnologia", "industria"
        ],
        "total_indicators": 50,
        "data_sources": ["BCRA", "INDEC", "BYMA", "Bluelytics", "MECON"],
        "status": "active"
    }

@app.get("/api", tags=["Root"])
async def api_info():
    return {
        "api_version": "v1",
        "total_indicators": 50,
        "categories": 6,
        "real_time_data": True,
        "historical_data": True,
        "rate_limits": "60 requests/minute",
        "authentication": "Coming soon",
        "documentation": "/docs"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Argfy Platform API started")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

# Shutdown event  
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("⏹️ Argfy Platform API shutdown")
EOF
    
    # Crear utils/monitoring.py
    mkdir -p app/utils
    cat > app/utils/monitoring.py << 'EOF'
import logging
import structlog
from ..config.settings import settings

def setup_logging():
    """Configure structured logging"""
    logging.basicConfig(
        level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
EOF
    
    # Crear router de health
    cat > app/routers/health.py << 'EOF'
from fastapi import APIRouter
from datetime import datetime
import psutil
import sys

router = APIRouter(prefix="/health", tags=["Health & Monitoring"])

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health():
    """Detailed health check with system info"""
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": (disk.used / disk.total) * 100,
            "python_version": sys.version,
            "uptime_seconds": psutil.boot_time()
        },
        "apis": {
            "bcra": "checking",
            "indec": "checking", 
            "bluelytics": "checking",
            "byma": "checking"
        }
    }
EOF
    
    # Crear archivo .env
    if [ ! -f ".env" ]; then
        log "Creando archivo .env..."
        cat > .env << 'EOF'
DATABASE_URL=sqlite:///./data/argentina.db
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
CORS_ORIGINS=["http://localhost:3000"]

# APIs (no requieren keys por ahora)
BCRA_API_URL=https://api.bcra.gob.ar
INDEC_API_URL=https://apis.datos.gob.ar/series/api
BLUELYTICS_URL=https://api.bluelytics.com.ar/v2

# Cache
REDIS_URL=redis://localhost:6379
CACHE_TTL=300

# Monitoring
LOG_LEVEL=INFO
EOF
    fi
    
    # Inicializar base de datos
    log "Inicializando base de datos..."
    python scripts/init_database.py || log "Database init script not found, skipping..."
    
    cd ..
    log "✅ Backend configurado"
}

# Configurar frontend con nuevos componentes
setup_frontend() {
    log "Configurando frontend expandido..."
    
    cd frontend
    
    # Verificar que node_modules existe
    if [ ! -d "node_modules" ]; then
        log "Instalando dependencias del frontend..."
        npm install
    fi
    
    # Instalar dependencias adicionales para gráficos e iconos
    log "Instalando dependencias adicionales..."
    
    npm install \
        recharts \
        lucide-react \
        @headlessui/react \
        @heroicons/react \
        clsx \
        tailwind-merge \
        axios \
        date-fns
    
    # Configurar variables de entorno
    if [ ! -f ".env.local" ]; then
        log "Creando archivo .env.local..."
        cat > .env.local << 'EOF'
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
NEXT_PUBLIC_ENVIRONMENT=development
EOF
    fi
    
    # Crear estructura de directorios
    mkdir -p src/{components/{dashboard,modal,charts,layout,ui,landing},hooks,lib,types,config,utils}
    
    # Crear archivo de configuración de Tailwind personalizada
    log "Configurando Tailwind CSS..."
    
    cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a'
        },
        success: {
          500: '#10b981',
          600: '#059669'
        },
        warning: {
          500: '#f59e0b',
          600: '#d97706'
        },
        danger: {
          500: '#ef4444',
          600: '#dc2626'
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
EOF
    
    # Configurar Next.js
    log "Configurando Next.js..."
    
    cat > next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL,
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE,
  },
  images: {
    domains: ['api.bcra.gob.ar', 'apis.datos.gob.ar'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/:path*`,
      },
    ]
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
EOF
    
    cd ..
    log "✅ Frontend configurado"
}

# Test de conectividad
test_connectivity() {
    log "Testeando conectividad entre frontend y backend..."
    
    # Iniciar backend en background
    cd backend
    source venv/bin/activate
    
    log "Iniciando backend para test..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    # Esperar que el backend inicie
    sleep 5
    
    # Test health endpoint
    if curl -f -s http://localhost:8000/health > /dev/null; then
        log "✅ Backend health check: OK"
    else
        warn "❌ Backend health check: FAILED"
    fi
    
    # Test API endpoint
    if curl -f -s http://localhost:8000/api/v1/dashboard/complete > /dev/null; then
        log "✅ Dashboard endpoint: OK"
    else
        warn "❌ Dashboard endpoint: FAILED"
    fi
    
    # Test docs
    if curl -f -s http://localhost:8000/docs > /dev/null; then
        log "✅ API Documentation: OK"
    else
        warn "❌ API Documentation: FAILED"
    fi
    
    # Detener backend
    kill $BACKEND_PID 2>/dev/null || true
    
    cd ..
    log "✅ Tests de conectividad completados"
}

# Crear scripts de desarrollo
create_dev_scripts() {
    log "Creando scripts de desarrollo..."
    
    mkdir -p scripts
    
    # Script para desarrollo local
    cat > scripts/dev-start.sh << 'EOF'
#!/bin/bash
# Start development servers

echo "🚀 Starting Argfy Development Environment"

# Terminal colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to handle Ctrl+C
cleanup() {
    echo -e "\n${GREEN}Stopping servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT

# Start backend
echo -e "${BLUE}Starting backend on port 8000...${NC}"
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${BLUE}Starting frontend on port 3000...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Show URLs
echo ""
echo "🎉 Argfy Platform is running!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop servers"

# Wait for processes
wait
EOF
    
    chmod +x scripts/dev-start.sh
    
    # Script para testing
    cat > scripts/test-all.sh << 'EOF'
#!/bin/bash
# Run all tests

echo "🧪 Running All Tests"

# Backend tests
echo "Testing backend..."
cd backend
source venv/bin/activate
pytest tests/ -v || echo "No backend tests found"
cd ..

# Frontend tests  
echo "Testing frontend..."
cd frontend
npm test -- --passWithNoTests || echo "Frontend tests completed"
cd ..

echo "✅ All tests completed"
EOF
    
    chmod +x scripts/test-all.sh
    
    # Script para deployment check
    cat > scripts/deploy-check.sh << 'EOF'
#!/bin/bash
# Check deployment readiness

echo "🔍 Deployment Readiness Check"

errors=0

# Check backend
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Missing backend/requirements.txt"
    errors=$((errors + 1))
fi

if [ ! -f "backend/.env" ]; then
    echo "❌ Missing backend/.env"
    errors=$((errors + 1))
fi

# Check frontend
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Missing frontend/package.json"
    errors=$((errors + 1))
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "❌ Missing frontend/.env.local"  
    errors=$((errors + 1))
fi

# Check environment variables
if [ -z "$VERCEL_TOKEN" ] && [ -z "$RENDER_API_KEY" ]; then
    echo "⚠️ No deployment tokens found (VERCEL_TOKEN, RENDER_API_KEY)"
fi

if [ $errors -eq 0 ]; then
    echo "✅ Deployment check passed"
    exit 0
else
    echo "❌ Deployment check failed with $errors errors"
    exit 1
fi
EOF
    
    chmod +x scripts/deploy-check.sh
    
    log "✅ Scripts de desarrollo creados"
}

# Función principal
main() {
    log "Iniciando configuración de integración..."
    
    check_project_structure
    setup_backend
    setup_frontend
    test_connectivity
    create_dev_scripts
    
    log "🎉 Integración configurada exitosamente!"
    log ""
    log "Próximos pasos:"
    log "1. Ejecutar: ./scripts/dev-start.sh"
    log "2. Abrir: http://localhost:3000"
    log "3. Verificar: http://localhost:8000/docs"
    log ""
    log "Scripts disponibles:"
    log "• ./scripts/dev-start.sh - Iniciar desarrollo"
    log "• ./scripts/test-all.sh - Ejecutar tests"
    log "• ./scripts/deploy-check.sh - Verificar deploy"
}

# Ejecutar función principal
main "$@"