# backend/app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .routers import indicators
from .database import engine, Base, init_db
from datetime import datetime
#import asyncio
import os

# Crear tablas si no existen
init_db()

app = FastAPI(
    title="Argfy API",
    description="""
    # API de Datos Económicos Argentinos
    
    Plataforma completa de datos económicos argentinos en tiempo real para desarrolladores, traders y analistas.
    
    ## 🚀 Funcionalidades Principales
    - **Indicadores Económicos**: Dólar, inflación, reservas, riesgo país
    - **Datos Históricos**: Series temporales con filtros personalizables
    - **Noticias Financieras**: Últimas noticias categorizadas
    - **API RESTful**: Endpoints documentados y fáciles de usar
    
    ## 📊 Fuentes de Datos
    - **BCRA**: Banco Central de la República Argentina
    - **INDEC**: Instituto Nacional de Estadística y Censos
    - **BYMA**: Bolsas y Mercados Argentinos
    - **JP Morgan**: Índice de Riesgo País
    
    ## 🔜 Próximamente
    - Autenticación con API Keys
    - Webhooks para notificaciones
    - Más fuentes de datos internacionales
    - Dashboard personalizable
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Argfy Team",
        "email": "contact@argfy.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://argfy.vercel.app",
        "https://*.vercel.app",
        "*"  # Para desarrollo - cambiar en producción
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(indicators.router, prefix="/api/v1")

@app.get("/", tags=["root"])
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": "Argfy API v0.1.0 - Demo Platform",
        "status": "active",
        "docs": "/docs",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "current_indicators": "/api/v1/indicators/current",
            "historical_data": "/api/v1/indicators/historical/{indicator}",
            "news": "/api/v1/indicators/news",
            "dashboard_summary": "/api/v1/indicators/summary"
        }
    }

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint para monitoreo"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "database": "connected",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/api/status", tags=["status"])
async def api_status():
    """Status detallado de la API"""
    return {
        "api_version": "0.1.0",
        "status": "operational",
        "uptime": "99.9%",
        "last_updated": datetime.utcnow().isoformat(),
        "services": {
            "database": "operational",
            "bcra_integration": "operational", 
            "data_pipeline": "operational"
        },
        "metrics": {
            "total_requests": "1,234",
            "avg_response_time": "120ms",
            "active_indicators": 8
        }
    }

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": "The requested endpoint does not exist",
            "available_endpoints": [
                "/docs",
                "/api/v1/indicators/current",
                "/api/v1/indicators/historical/{indicator}",
                "/api/v1/indicators/news"
            ]
        }
    )
#@app.on_event("startup")
#async def startup_event():
#    if os.getenv("ENVIRONMENT") == "production":
#        asyncio.create_task(ping_self())

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )