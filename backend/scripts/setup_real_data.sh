#!/bin/bash
# backend/scripts/setup_real_data.sh
# Script para configurar automáticamente los datos reales en Argfy Platform

set -e

echo "🚀 Argfy Platform - Setup de Datos Reales"
echo "=========================================="

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] ⚠️  $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] ❌ $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[INFO] ℹ️  $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "app/main.py" ]; then
    error "Ejecuta este script desde el directorio backend/"
fi

# Función para verificar dependencias
check_dependencies() {
    log "Verificando dependencias del sistema..."
    
    if ! command -v python3 &> /dev/null; then
        error "Python 3 no está instalado"
    fi
    
    if ! command -v pip &> /dev/null; then
        error "pip no está instalado"
    fi
    
    # Verificar Redis (opcional)
    if command -v redis-server &> /dev/null; then
        log "Redis encontrado - caching habilitado"
    else
        warn "Redis no encontrado - caching deshabilitado"
        info "Para instalar Redis:"
        info "  Ubuntu/Debian: sudo apt install redis-server"
        info "  macOS: brew install redis"
        info "  CentOS/RHEL: sudo yum install redis"
    fi
    
    log "Dependencias verificadas"
}

# Activar entorno virtual
setup_venv() {
    log "Configurando entorno virtual..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log "Entorno virtual creado"
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    
    log "Entorno virtual activado"
}

# Instalar dependencias
install_dependencies() {
    log "Instalando dependencias para datos reales..."
    
    # Crear requirements con dependencias necesarias para datos reales
    cat > requirements_real_data.txt << 'EOF'
# Dependencias existentes
fastapi[all]==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pandas==2.1.3
requests==2.31.0
python-multipart==0.0.6
python-dotenv==1.0.0

# Para testing
pytest==7.4.3
httpx==0.25.2

# Para datos reales - NUEVAS DEPENDENCIAS
aiohttp==3.9.1
beautifulsoup4==4.12.2
lxml==4.9.3
redis==5.0.1
psutil==5.9.6

# Para scraping y parsing
scrapy==2.11.0
requests-html==0.10.0

# Para trabajo con fechas y time zones
python-dateutil==2.8.2
pytz==2023.3

# Para monitoreo (opcional)
sentry-sdk==1.38.0

# Para validación de datos
pydantic==2.5.0

# Para trabajo con JSON y APIs
orjson==3.9.10
EOF
    
    pip install -r requirements_real_data.txt
    log "Dependencias instaladas"
}

# Configurar archivo .env
setup_env_file() {
    log "Configurando archivo de variables de entorno..."
    
    if [ ! -f ".env" ]; then
        # Crear .env con configuración básica
        cat > .env << 'EOF'
# Configuración básica - Argfy Platform
DATABASE_URL=sqlite:///./data/argentina.db
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production-$(date +%s)
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://argfy.vercel.app"]

# APIs Argentina (no requieren key)
BCRA_API_URL=https://api.bcra.gob.ar
INDEC_API_URL=https://apis.datos.gob.ar/series/api
BLUELYTICS_URL=https://api.bluelytics.com.ar/v2
DOLAR_API_URL=https://dolarapi.com/v1

# Cache y performance
REDIS_URL=redis://localhost:6379
CACHE_TTL=300
API_RATE_LIMIT=60
REQUEST_TIMEOUT=10

# Feature flags
ENABLE_REAL_DATA=true
ENABLE_CACHING=true
ENABLE_SCRAPING=true

# APIs con key (agregar manualmente)
ALPHA_VANTAGE_API_KEY=
FIXER_API_KEY=
BYMA_API_KEY=
EOF
        log "Archivo .env creado con configuración básica"
    else
        warn "Archivo .env ya existe - no se sobrescribió"
    fi
}

# Crear directorios necesarios
create_directories() {
    log "Creando directorios necesarios..."
    
    mkdir -p data
    mkdir -p logs
    mkdir -p scripts
    mkdir -p app/services
    mkdir -p tests
    
    log "Directorios creados"
}

# Copiar servicios de datos reales
copy_real_services() {
    log "Configurando servicios de datos reales..."
    
    info "IMPORTANTE: Los siguientes archivos deben ser copiados al proyecto:"
    info "1. app/services/bcra_real_service.py"
    info "2. app/services/dolar_blue_service.py" 
    info "3. app/services/integrated_data_service.py"
    info "4. scripts/test_apis.py"
    
    # Crear archivo de configuración para importar servicios
    cat > app/services/__init__.py << 'EOF'
# Services initialization
from .bcra_real_service import BCRARealService
from .dolar_blue_service import DolarBlueService
from .integrated_data_service import IntegratedDataService

__all__ = ["BCRARealService", "DolarBlueService", "IntegratedDataService"]
EOF
    
    log "Servicios configurados"
}

# Actualizar el router principal
update_router() {
    log "Actualizando router para usar datos reales..."
    
    # Crear backup del router actual
    if [ -f "app/routers/indicators.py" ]; then
        cp app/routers/indicators.py app/routers/indicators.py.backup
        log "Backup del router actual creado"
    fi
    
    # Crear nuevo router con datos reales
    cat > app/routers/indicators_real.py << 'EOF'
# backend/app/routers/indicators_real.py
"""
Router actualizado con datos reales para Argfy Platform
Reemplaza los datos demo con datos reales de múltiples APIs
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import EconomicIndicator, HistoricalData, NewsItem
from ..services.integrated_data_service import IntegratedDataService
from datetime import datetime, timedelta
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/indicators", tags=["indicators"])

@router.get("/current")
async def get_current_indicators(db: Session = Depends(get_db)):
    """Obtiene indicadores económicos actuales usando datos reales"""
    try:
        # Usar servicio integrado para datos reales
        async with IntegratedDataService() as service:
            real_indicators = await service.get_all_current_indicators()
            
            # Limpiar indicadores existentes
            db.query(EconomicIndicator).filter(
                EconomicIndicator.is_active == True
            ).update({"is_active": False})
            
            # Insertar nuevos datos reales
            db_indicators = []
            for indicator_data in real_indicators:
                db_indicator = EconomicIndicator(**indicator_data.to_indicator_dict())
                db.add(db_indicator)
                db_indicators.append(db_indicator)
            
            db.commit()
            
            # Convertir a formato de respuesta
            response_data = []
            for indicator in db_indicators:
                response_data.append({
                    "id": indicator.id,
                    "indicator_type": indicator.indicator_type,
                    "value": indicator.value,
                    "date": indicator.date.isoformat(),
                    "source": indicator.source,
                    "is_active": indicator.is_active
                })
            
            return {
                "data": response_data,
                "timestamp": datetime.utcnow().isoformat(),
                "count": len(response_data),
                "status": "success",
                "data_source": "real_apis"
            }
            
    except Exception as e:
        logger.error(f"Error fetching real indicators: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching indicators: {str(e)}"
        )

@router.get("/historical/{indicator_type}")
async def get_historical_data(
    indicator_type: str, 
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obtiene datos históricos reales de un indicador específico"""
    try:
        async with IntegratedDataService() as service:
            historical_data = await service.get_historical_data(indicator_type, days)
            
            # Si tenemos datos reales, usarlos
            if historical_data:
                return {
                    "indicator": indicator_type,
                    "data": historical_data,
                    "period": f"{days} days",
                    "count": len(historical_data),
                    "status": "success",
                    "data_source": "real_apis"
                }
            
            # Fallback a datos de la DB si no hay datos reales
            start_date = datetime.utcnow() - timedelta(days=days)
            
            db_data = db.query(HistoricalData).filter(
                HistoricalData.indicator_id == indicator_type,
                HistoricalData.date >= start_date
            ).order_by(HistoricalData.date.asc()).all()
            
            chart_data = []
            for item in db_data:
                chart_data.append({
                    "date": item.date.strftime("%Y-%m-%d"),
                    "value": item.value,
                    "source": item.source
                })
            
            return {
                "indicator": indicator_type,
                "data": chart_data,
                "period": f"{days} days",
                "count": len(chart_data),
                "status": "success",
                "data_source": "database_fallback"
            }
            
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching historical data: {str(e)}"
        )

@router.get("/news")
async def get_news(
    limit: int = Query(6, ge=1, le=20),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtiene noticias económicas (mantiene funcionalidad existente)"""
    try:
        query = db.query(NewsItem)
        
        if category:
            query = query.filter(NewsItem.category == category.upper())
            
        news = query.order_by(NewsItem.published_at.desc()).limit(limit).all()
        
        # Si no hay noticias, generar algunas demo
        if not news:
            from ..services.bcra_service import generate_demo_news
            demo_news = generate_demo_news()
            for item in demo_news:
                news_item = NewsItem(**item)
                db.add(news_item)
            db.commit()
            
            news = query.order_by(NewsItem.published_at.desc()).limit(limit).all()
        
        news_data = []
        for item in news:
            news_data.append({
                "id": item.id,
                "title": item.title,
                "summary": item.summary,
                "category": item.category,
                "source": item.source,
                "published_at": item.published_at.isoformat(),
                "is_featured": item.is_featured
            })
        
        return {
            "data": news_data,
            "count": len(news_data),
            "category": category,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@router.get("/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Obtiene resumen completo para el dashboard usando datos reales"""
    try:
        # Obtener indicadores actuales (que ya son reales)
        indicators_response = await get_current_indicators(db)
        
        # Obtener noticias
        news_response = await get_news(limit=3, db=db)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "indicators": {
                "count": indicators_response["count"],
                "data": indicators_response["data"]
            },
            "news": {
                "count": news_response["count"], 
                "featured": news_response["data"]
            },
            "status": "success",
            "data_source": "real_apis"
        }
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@router.post("/refresh")
async def refresh_indicators(db: Session = Depends(get_db)):
    """Actualiza todos los indicadores con datos reales frescos"""
    try:
        async with IntegratedDataService() as service:
            refresh_result = await service.refresh_all_data()
            
            if refresh_result["success"]:
                # Obtener datos actualizados
                real_indicators = await service.get_all_current_indicators()
                
                # Desactivar indicadores existentes
                db.query(EconomicIndicator).update({"is_active": False})
                
                # Insertar nuevos datos
                for indicator_data in real_indicators:
                    db_indicator = EconomicIndicator(**indicator_data.to_indicator_dict())
                    db.add(db_indicator)
                
                db.commit()
                
                return {
                    "message": "Indicators refreshed successfully with real data",
                    "timestamp": datetime.utcnow().isoformat(),
                    "refresh_stats": refresh_result,
                    "status": "success"
                }
            else:
                return {
                    "message": "Refresh completed with errors",
                    "error": refresh_result.get("error"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "partial_success"
                }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error refreshing data: {e}")
        raise HTTPException(status_code=500, detail=f"Error refreshing data: {str(e)}")

# Nuevo endpoint para estadísticas de datos reales
@router.get("/data-sources")
async def get_data_sources():
    """Obtiene información sobre las fuentes de datos disponibles"""
    return {
        "sources": {
            "bcra": {
                "name": "Banco Central de la República Argentina",
                "url": "https://api.bcra.gob.ar",
                "indicators": ["dolar_oficial", "reservas_bcra", "tasa_bcra", "base_monetaria"],
                "status": "active",
                "free": True
            },
            "bluelytics": {
                "name": "Bluelytics",
                "url": "https://api.bluelytics.com.ar",
                "indicators": ["dolar_blue", "dolar_oficial"],
                "status": "active", 
                "free": True
            },
            "indec": {
                "name": "Instituto Nacional de Estadística y Censos",
                "url": "https://apis.datos.gob.ar",
                "indicators": ["inflacion_mensual", "emae"],
                "status": "active",
                "free": True
            },
            "yahoo_finance": {
                "name": "Yahoo Finance",
                "url": "https://finance.yahoo.com",
                "indicators": ["merval"],
                "status": "active",
                "free": True
            }
        },
        "last_updated": datetime.utcnow().isoformat(),
        "total_sources": 4,
        "real_data_enabled": True
    }

# Endpoint de salud para datos reales
@router.get("/health-check")
async def health_check():
    """Verifica el estado de todas las fuentes de datos"""
    try:
        async with IntegratedDataService() as service:
            # Test rápido de conectividad
            indicators = await service.get_all_current_indicators()
            
            sources_status = {}
            for indicator in indicators:
                source = indicator.source
                if source not in sources_status:
                    sources_status[source] = {
                        "indicators_count": 0,
                        "status": "healthy"
                    }
                sources_status[source]["indicators_count"] += 1
            
            return {
                "overall_status": "healthy",
                "sources": sources_status,
                "total_indicators": len(indicators),
                "timestamp": datetime.utcnow().isoformat(),
                "real_data_enabled": True
            }
            
    except Exception as e:
        return {
            "overall_status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "real_data_enabled": False
        }
EOF
    
    info "Nuevo router con datos reales creado: app/routers/indicators_real.py"
    info "Para activarlo, reemplaza indicators.py por indicators_real.py"
}

# Crear scripts de testing
create_test_scripts() {
    log "Creando scripts de testing..."
    
    # Script de test básico
    cat > scripts/test_real_data.py << 'EOF'
#!/usr/bin/env python3
"""
Script de test rápido para verificar que los datos reales funcionan
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.integrated_data_service import IntegratedDataService

async def quick_test():
    print("🧪 Testing Real Data Services...")
    
    try:
        async with IntegratedDataService() as service:
            indicators = await service.get_all_current_indicators()
            
            print(f"✅ Successfully fetched {len(indicators)} indicators")
            
            # Show sample data
            for indicator in indicators[:5]:
                print(f"  📊 {indicator.indicator_type}: {indicator.value} ({indicator.source})")
            
            if len(indicators) > 5:
                print(f"  ... and {len(indicators) - 5} more")
                
            print("\n🎉 Real data is working!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)
EOF
    
    chmod +x scripts/test_real_data.py
    log "Scripts de testing creados"
}

# Función principal
main() {
    log "Iniciando configuración de datos reales para Argfy Platform"
    
    check_dependencies
    setup_venv
    install_dependencies
    create_directories
    setup_env_file
    copy_real_services
    update_router
    create_test_scripts
    
    echo ""
    log "🎉 Setup de datos reales completado!"
    echo ""
    info "PRÓXIMOS PASOS:"
    info "1. Copia los archivos de servicios listados anteriormente"
    info "2. Obtén API keys gratuitas:"
    info "   - Alpha Vantage: https://www.alphavantage.co/support/#api-key"
    info "   - Fixer.io: https://fixer.io/signup/free"
    info "3. Actualiza el archivo .env con tus API keys"
    info "4. Ejecuta: python scripts/test_real_data.py"
    info "5. Si el test pasa, reemplaza indicators.py por indicators_real.py"
    echo ""
    warn "RECUERDA: Sin API keys algunas fuentes usarán datos demo como fallback"
    warn "REDIS: Para mejor performance, instala Redis para caching"
    echo ""
    log "🚀 ¡Tu plataforma estará usando datos económicos reales!"
}

# Ejecutar función principal
main "$@"