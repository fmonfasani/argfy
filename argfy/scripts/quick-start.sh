#!/bin/bash
# scripts/quick-start.sh - Windows Compatible
# Script de inicio rápido para desarrollo

set -e

echo "Argfy Platform - Quick Start"
echo "================================"

# Colores
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

# Función para verificar dependencias
check_dependencies() {
    log "Verificando dependencias..."
    
    # Verificar Python (adaptado para Windows)
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        error "Python no esta instalado. Instalar desde: https://www.python.org/downloads/"
    fi
    
    if ! command -v node &> /dev/null; then
        error "Node.js no esta instalado. Instalar desde: https://nodejs.org/"
    fi
    
    if ! command -v npm &> /dev/null; then
        error "npm no esta instalado"
    fi
    
    log "Dependencias verificadas - Python: $PYTHON_CMD"
}

# Configurar backend
setup_backend() {
    log "Configurando backend..."
    
    cd backend
    
    # Crear entorno virtual si no existe
    if [ ! -d ".venv" ]; then
        log "Creando entorno virtual..."
        $PYTHON_CMD -m venv .venv
    fi
    
    # Activar entorno virtual (Windows)
    log "Activando entorno virtual..."
    source .venv/Scripts/activate
    
    # Actualizar pip
    python -m pip install --upgrade pip
    
    # Instalar dependencias básicas
    log "Instalando dependencias del backend..."
    pip install sqlalchemy==2.0.23
    pip install fastapi==0.104.1
    pip install uvicorn==0.24.0
    pip install requests==2.31.0
    pip install python-dotenv==1.0.0
    pip install python-multipart==0.0.6
    
    # Crear archivo .env si no existe
    if [ ! -f ".env" ]; then
        log "Creando archivo .env..."
        cat > .env << ENVEOF
DATABASE_URL=sqlite:///./data/argentina.db
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
CORS_ORIGINS=["http://localhost:3000"]
ENVEOF
    fi
    
    # Crear directorios necesarios
    mkdir -p logs data
    
    # Inicializar base de datos
    if [ -f "scripts/simple_init.py" ]; then
        log "Inicializando base de datos..."
        python scripts/simple_init.py
    else
        warn "Script de inicializacion no encontrado"
    fi
    
    cd ..
    log "Backend configurado"
}

# Configurar frontend
setup_frontend() {
    log "Configurando frontend..."
    
    cd frontend
    
    # Instalar dependencias
    log "Instalando dependencias del frontend..."
    npm install
    
    # Crear archivo .env.local si no existe
    if [ ! -f ".env.local" ]; then
        log "Creando archivo .env.local..."
        cat > .env.local << ENVEOF
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
ENVEOF
    fi
    
    cd ..
    log "Frontend configurado"
}

# Función para iniciar servicios
start_services() {
    log "Iniciando servicios..."
    
    # Verificar que los directorios existen
    if [ ! -d "backend/.venv" ]; then
        error "Entorno virtual no encontrado. Ejecuta: setup primero"
    fi
    
    if [ ! -d "frontend/node_modules" ]; then
        error "Node modules no encontrado. Ejecuta: setup primero"
    fi
    
    # Función para manejar Ctrl+C
    cleanup() {
        log "Deteniendo servicios..."
        taskkill //F //IM "python.exe" 2>/dev/null || true
        taskkill //F //IM "node.exe" 2>/dev/null || true
        exit 0
    }
    trap cleanup SIGINT
    
    # Iniciar backend
    log "Iniciando backend en puerto 8000..."
    cd backend
    source .venv/Scripts/activate
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
    
    # Esperar un poco para que el backend inicie
    sleep 5
    
    # Iniciar frontend
    log "Iniciando frontend..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # Mostrar información
    echo ""
    echo "Argfy Platform esta ejecutandose!"
    echo ""
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo "Health Check: http://localhost:8000/health"
    echo ""
    echo "Presiona Ctrl+C para detener los servicios"
    
    # Esperar
    wait
}

# Función principal
main() {
    case "${1:-start}" in
        "setup")
            check_dependencies
            setup_backend
            setup_frontend
            log "Setup completado! Ejecuta: ./scripts/quick-start.sh start"
            ;;
        "start")
            start_services
            ;;
        "reset")
            log "Reseteando proyecto..."
            rm -rf backend/.venv frontend/node_modules backend/data frontend/.next
            rm -f backend/.env frontend/.env.local
            log "Proyecto reseteado. Ejecuta 'setup' para reconfigurar"
            ;;
        *)
            echo "Uso: $0 [comando]"
            echo ""
            echo "Comandos disponibles:"
            echo "  setup    - Configurar el proyecto por primera vez"
            echo "  start    - Iniciar los servicios"
            echo "  reset    - Resetear el proyecto"
            echo ""
            ;;
    esac
}

# Ejecutar función principal
main "$@"
