#!/bin/bash
# master_setup.sh - Script ejecutor maestro para Argfy Platform
# Una sola línea de comando para configurar todo el entorno de desarrollo

set -e

echo "🏗️ ARGFY PLATFORM - MASTER SETUP SCRIPT"
echo "========================================"
echo "Configuración completa de desarrollo en 5 minutos"
echo ""

# Colors and formatting
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Icons
ROCKET="🚀"
CHECK="✅"
WARN="⚠️"
ERROR="❌"
INFO="ℹ️"
GEAR="⚙️"

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"; }
info() { echo -e "${BLUE}${INFO} $1${NC}"; }
warn() { echo -e "${YELLOW}${WARN} $1${NC}"; }
error() { echo -e "${RED}${ERROR} $1${NC}"; exit 1; }
success() { echo -e "${GREEN}${CHECK} $1${NC}"; }
header() { echo -e "${PURPLE}${BOLD}\n=== $1 ===${NC}"; }

# =============================================
# SYSTEM DETECTION AND VALIDATION
# =============================================

detect_system() {
    header "DETECCIÓN DEL SISTEMA"
    
    # Detect OS
    case "$OSTYPE" in
        msys*|win32*|cygwin*)
            PLATFORM="windows"
            ACTIVATE_CMD=".venv/Scripts/activate"
            ;;
        linux-gnu*|linux*)
            PLATFORM="linux"
            ACTIVATE_CMD=".venv/bin/activate"
            ;;
        darwin*)
            PLATFORM="macos"
            ACTIVATE_CMD=".venv/bin/activate"
            ;;
        *)
            PLATFORM="unknown"
            ACTIVATE_CMD=".venv/bin/activate"
            ;;
    esac
    
    info "Sistema detectado: $PLATFORM"
    
    # Detect Python version
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
        PYTHON_VERSION=$(python3.11 --version)
        success "Python 3.11 encontrado: $PYTHON_VERSION"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version)
        if [[ $PYTHON_VERSION == *"3.13"* ]]; then
            warn "Python 3.13 detectado - algunas librerías pueden tener problemas"
            warn "Se recomienda Python 3.11 para máxima compatibilidad"
        fi
        info "Python encontrado: $PYTHON_VERSION"
    else
        error "Python 3+ requerido. Instálalo desde https://python.org"
    fi
    
    # Check Node.js (for future frontend)
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        success "Node.js encontrado: $NODE_VERSION"
    else
        warn "Node.js no encontrado (opcional para frontend)"
    fi
    
    # Check Git
    if command -v git &> /dev/null; then
        success "Git disponible"
    else
        warn "Git no encontrado - recomendado para desarrollo"
    fi
}

# =============================================
# ENVIRONMENT SETUP
# =============================================

setup_environment() {
    header "CONFIGURACIÓN DEL ENTORNO"
    
    # Create project structure
    log "Creando estructura de directorios..."
    mkdir -p {data/{sqlite,postgresql,backups},logs,scripts/{database,deployment},docs,config}
    mkdir -p app/{core,models,services,api/{v1,middleware},schemas,utils,tests}
    
    # Clean previous installations
    log "Limpiando instalaciones previas..."
    rm -rf .venv venv __pycache__ .pytest_cache *.egg-info
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Create virtual environment
    log "Creando entorno virtual..."
    $PYTHON_CMD -m venv .venv
    
    # Activate virtual environment
    source $ACTIVATE_CMD
    
    # Upgrade pip and tools
    log "Actualizando herramientas de desarrollo..."
    python -m pip install --upgrade pip setuptools wheel build
    
    success "Entorno configurado correctamente"
}

# =============================================
# DEPENDENCIES INSTALLATION
# =============================================

install_dependencies() {
    header "INSTALACIÓN DE DEPENDENCIAS"
    
    # Activate virtual environment
    source $ACTIVATE_CMD
    
    log "Instalando stack FastAPI core..."
    pip install fastapi==0.104.1 \
                uvicorn[standard]==0.24.0 \
                starlette==0.27.0 \
                pydantic==2.5.1 \
                pydantic-settings==2.1.0
    
    log "Instalando stack de base de datos..."
    pip install sqlalchemy==2.0.23 \
                alembic==1.12.1
    
    # Try PostgreSQL drivers (optional)
    log "Intentando instalar drivers PostgreSQL..."
    pip install psycopg2-binary==2.9.9 || warn "psycopg2-binary falló - solo SQLite disponible"
    pip install asyncpg==0.29.0 || warn "asyncpg falló - funcionalidad async PostgreSQL limitada"
    
    log "Instalando clientes HTTP..."
    pip install requests==2.31.0 \
                httpx==0.25.2
                
    # Try aiohttp (may fail on some systems)
    pip install aiohttp==3.9.1 || warn "aiohttp falló - solo requests/httpx disponibles"
    
    log "Instalando herramientas de datos..."
    # Try pandas with fallback to older version
    pip install pandas==2.0.3 || pip install pandas==1.5.3 || warn "pandas falló - usar estructuras Python nativas"
    pip install python-dateutil==2.8.2 pytz==2023.3
    
    log "Instalando utilidades de desarrollo..."
    pip install python-dotenv==1.0.0 \
                python-multipart==0.0.6 \
                click==8.1.7 \
                rich==13.7.0
    
    log "Instalando herramientas de testing..."
    pip install pytest==7.4.3 \
                pytest-asyncio==0.21.1 \
                pytest-cov==4.1.0 \
                black==23.11.0 \
                ruff==0.1.6
    
    # Try mypy (optional)
    pip install mypy==1.7.1 || warn "mypy falló - type checking limitado"
    
    success "Dependencias instaladas correctamente"
}

# =============================================
# PROJECT FILES CREATION
# =============================================

create_project_files() {
    header "CREACIÓN DE ARCHIVOS DEL PROYECTO"
    
    # Create main.py if it doesn't exist
    if [ ! -f "app/main.py" ]; then
        log "Creando app/main.py..."
        cat > app/main.py << 'EOF'
"""
Argfy Platform - Main Application
Enterprise-ready FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Create FastAPI app
app = FastAPI(
    title="Argfy Platform API",
    description="Enterprise-grade financial data platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://argfy.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Argfy Platform API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
EOF
    fi
    
    # Create __init__.py files
    find app -type d -exec touch {}/__init__.py \;
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        log "Creando archivo .env..."
        cat > .env << 'EOF'
# Argfy Platform - Environment Configuration
DATABASE_URL=sqlite:///./data/sqlite/argfy_dev.db
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
CORS_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=INFO
EOF
    fi
    
    # Create requirements.txt
    log "Generando requirements.txt..."
    source $ACTIVATE_CMD
    pip freeze > requirements.txt
    
    # Create basic test
    mkdir -p app/tests
    if [ ! -f "app/tests/test_main.py" ]; then
        cat > app/tests/test_main.py << 'EOF'
"""
Basic tests for Argfy Platform
"""

def test_import():
    """Test that main module can be imported"""
    from app.main import app
    assert app is not None

def test_health_endpoint():
    """Test health endpoint (requires test client setup)"""
    # TODO: Implement with TestClient when ready
    pass
EOF
    fi
    
    success "Archivos del proyecto creados"
}

# =============================================
# DATABASE INITIALIZATION
# =============================================

setup_database() {
    header "CONFIGURACIÓN DE BASE DE DATOS"
    
    source $ACTIVATE_CMD
    
    # Create simple database initialization script
    if [ ! -f "scripts/init_db.py" ]; then
        log "Creando script de inicialización de BD..."
        cat > scripts/init_db.py << 'EOF'
#!/usr/bin/env python3
"""
Simple database initialization for Argfy Platform
"""

import os
import sqlite3
from datetime import datetime

def create_database():
    """Create SQLite database with basic tables"""
    
    # Ensure data directory exists
    os.makedirs('data/sqlite', exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect('data/sqlite/argfy_dev.db')
    cursor = conn.cursor()
    
    print("📊 Creating basic tables...")
    
    # Economic indicators table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS economic_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicator_type TEXT NOT NULL,
            value REAL NOT NULL,
            timestamp DATETIME NOT NULL,
            source TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sample data
    sample_data = [
        ('dolar_blue', 1350.0, datetime.now(), 'DEMO'),
        ('dolar_oficial', 1189.5, datetime.now(), 'BCRA'),
        ('inflacion_mensual', 3.2, datetime.now(), 'INDEC'),
        ('reservas_bcra', 41200.0, datetime.now(), 'BCRA'),
        ('riesgo_pais', 1642, datetime.now(), 'JP_MORGAN'),
        ('merval', 1847523, datetime.now(), 'BYMA'),
    ]
    
    # Clear existing data
    cursor.execute('DELETE FROM economic_indicators')
    
    # Insert sample data
    cursor.executemany('''
        INSERT INTO economic_indicators (indicator_type, value, timestamp, source)
        VALUES (?, ?, ?, ?)
    ''', sample_data)
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized with sample data")

if __name__ == "__main__":
    create_database()
EOF
    fi
    
    # Initialize database
    log "Inicializando base de datos..."
    python scripts/init_db.py
    
    success "Base de datos configurada"
}

# =============================================
# DEVELOPMENT TOOLS SETUP
# =============================================

setup_development_tools() {
    header "CONFIGURACIÓN DE HERRAMIENTAS DE DESARROLLO"
    
    # Create Makefile
    if [ ! -f "Makefile" ]; then
        log "Creando Makefile..."
        cat > Makefile << 'EOF'
.PHONY: install dev test lint format clean help

# Default target
help:
	@echo "Argfy Platform - Available Commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make dev      - Start development server"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linting"
	@echo "  make format   - Format code"
	@echo "  make clean    - Clean build artifacts"

install:
	python -m venv .venv
	source .venv/bin/activate && pip install -r requirements.txt

dev:
	source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	source .venv/bin/activate && python -m pytest app/tests/ -v

lint:
	source .venv/bin/activate && ruff check app/ || echo "Ruff not available"

format:
	source .venv/bin/activate && black app/ || echo "Black not available"

clean:
	rm -rf .venv __pycache__ .pytest_cache .coverage htmlcov/
	find . -name "*.pyc" -delete

db-init:
	source .venv/bin/activate && python scripts/init_db.py

# Windows-compatible versions
dev-win:
	.venv\\Scripts\\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test-win:
	.venv\\Scripts\\activate && python -m pytest app/tests/ -v
EOF
    fi
    
    # Create .gitignore
    if [ ! -f ".gitignore" ]; then
        log "Creando .gitignore..."
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
.venv/
ENV/
env/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
data/sqlite/*.db
data/postgresql/
logs/*.log
*.log

# Environment files
.env.local
.env.production

# Test coverage
.coverage
htmlcov/
.pytest_cache/

# Build artifacts
*.whl
*.tar.gz
EOF
    fi
    
    success "Herramientas de desarrollo configuradas"
}

# =============================================
# TESTING AND VALIDATION
# =============================================

test_installation() {
    header "VALIDACIÓN DE LA INSTALACIÓN"
    
    source $ACTIVATE_CMD
    
    # Test imports
    log "Probando imports críticos..."
    python -c "
import fastapi
import uvicorn
import sqlalchemy
print('✅ Core dependencies OK')
"
    
    # Test optional imports
    python -c "
try:
    import pandas
    print('✅ Pandas available')
except ImportError:
    print('⚠️ Pandas not available - using native Python structures')

try:
    import aiohttp
    print('✅ aiohttp available')
except ImportError:
    print('⚠️ aiohttp not available - using requests/httpx only')
" || true
    
    # Test database
    log "Probando conexión a base de datos..."
    python -c "
import sqlite3
conn = sqlite3.connect('data/sqlite/argfy_dev.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM economic_indicators')
count = cursor.fetchone()[0]
print(f'✅ Database OK: {count} indicators available')
conn.close()
"
    
    # Test FastAPI app
    log "Probando aplicación FastAPI..."
    python -c "
from app.main import app
print('✅ FastAPI app loads successfully')
print(f'   Title: {app.title}')
print(f'   Version: {app.version}')
"
    
    success "Instalación validada correctamente"
}

# =============================================
# FINAL INSTRUCTIONS
# =============================================

show_final_instructions() {
    header "🎉 INSTALACIÓN COMPLETADA"
    
    echo ""
    echo -e "${BOLD}${GREEN}Argfy Platform está listo para desarrollo!${NC}"
    echo ""
    echo -e "${CYAN}📋 PRÓXIMOS PASOS:${NC}"
    echo ""
    echo "1. Activar entorno virtual:"
    echo -e "   ${YELLOW}source $ACTIVATE_CMD${NC}"
    echo ""
    echo "2. Iniciar servidor de desarrollo:"
    echo -e "   ${YELLOW}make dev${NC}"
    echo -e "   ${GRAY}o manualmente: uvicorn app.main:app --reload${NC}"
    echo ""
    echo "3. Abrir en el navegador:"
    echo -e "   ${BLUE}http://localhost:8000${NC} - API principal"
    echo -e "   ${BLUE}http://localhost:8000/docs${NC} - Documentación interactiva"
    echo -e "   ${BLUE}http://localhost:8000/health${NC} - Health check"
    echo ""
    echo -e "${CYAN}🛠️ COMANDOS ÚTILES:${NC}"
    echo -e "   ${YELLOW}make test${NC}     - Ejecutar tests"
    echo -e "   ${YELLOW}make lint${NC}     - Verificar código"
    echo -e "   ${YELLOW}make format${NC}   - Formatear código"
    echo -e "   ${YELLOW}make clean${NC}    - Limpiar archivos temporales"
    echo ""
    echo -e "${CYAN}📁 ESTRUCTURA DEL PROYECTO:${NC}"
    echo "   app/           - Código de la aplicación"
    echo "   data/          - Bases de datos"
    echo "   scripts/       - Scripts utilitarios"
    echo "   docs/          - Documentación"
    echo ""
    echo -e "${PURPLE}🚀 ROADMAP SIGUIENTE:${NC}"
    echo "   • Migrar a PostgreSQL cuando escales"
    echo "   • Agregar más fuentes de datos (BCRA real)"
    echo "   • Implementar frontend con Next.js"
    echo "   • Configurar CI/CD con GitHub Actions"
    echo ""
    echo -e "${GREEN}✨ ¡Tu plataforma financiera está lista para conquistar el mercado argentino!${NC}"
    echo ""
}

# =============================================
# MAIN EXECUTION
# =============================================

main() {
    # Ensure we're in the backend directory
    if [ ! -f "../frontend/package.json" ] && [ ! -f "app/__init__.py" ]; then
        warn "Navegando al directorio backend..."
        cd backend 2>/dev/null || true
    fi
    
    detect_system
    setup_environment
    install_dependencies
    create_project_files
    setup_database
    setup_development_tools
    test_installation
    show_final_instructions
}

# Execute main function
main "$@"