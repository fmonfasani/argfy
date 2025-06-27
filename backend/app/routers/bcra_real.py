# backend/app/routers/bcra_real.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.bcra_real_data_service import BCRARealDataService
from datetime import datetime
import asyncio

router = APIRouter(prefix="/api/v1/bcra", tags=["BCRA Real Data"])

@router.get("/dashboard")
async def get_real_dashboard():
    """Obtener datos reales del dashboard BCRA"""
    async with BCRARealDataService() as service:
        dashboard_data = await service.get_dashboard_data()
        
        if dashboard_data.get("status") == "success":
            return {
                "status": "success",
                "data": dashboard_data,
                "timestamp": datetime.now().isoformat(),
                "source": "BCRA_REAL_TIME"
            }
        else:
            raise HTTPException(status_code=500, detail="Error obteniendo datos BCRA")

@router.get("/variables")
async def get_variables_monetarias():
    """Obtener todas las variables monetarias"""
    async with BCRARealDataService() as service:
        variables = await service.get_variables_monetarias()
        return variables

@router.get("/cotizaciones")
async def get_cotizaciones():
    """Obtener cotizaciones oficiales"""
    async with BCRARealDataService() as service:
        cotizaciones = await service.get_cotizaciones_oficiales()
        return cotizaciones

@router.get("/variable/{variable_id}/historica")
async def get_variable_historica(variable_id: int, dias: int = 30):
    """Obtener datos históricos de una variable"""
    async with BCRARealDataService() as service:
        historicos = await service.get_variable_historica(variable_id, dias)
        return historicos

@router.post("/refresh")
async def refresh_data(background_tasks: BackgroundTasks):
    """Forzar actualización de datos"""
    
    async def update_task():
        async with BCRARealDataService() as service:
            dashboard_data = await service.get_dashboard_data()
            if dashboard_data.get("status") == "success":
                await service.save_to_database(dashboard_data)
    
    background_tasks.add_task(update_task)
    
    return {
        "status": "success",
        "message": "Actualización iniciada en segundo plano",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health_check():
    """Verificar estado de las APIs del BCRA"""
    async with BCRARealDataService() as service:
        # Test rápido de conectividad
        variables = await service.get_variables_monetarias()
        cotizaciones = await service.get_cotizaciones_oficiales()
        
        return {
            "status": "healthy",
            "apis": {
                "variables_monetarias": variables.get("status") == "success",
                "cotizaciones": cotizaciones.get("status") == "success"
            },
            "timestamp": datetime.now().isoformat()
        }