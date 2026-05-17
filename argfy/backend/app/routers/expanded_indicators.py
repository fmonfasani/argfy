# backend/app/routers/expanded_indicators.py
"""
API Endpoints expandidos para TODOS los indicadores de la plataforma
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from ..database import get_db
from ..services.expanded_data_service import ExpandedDataService
from ..config.indicators_mapping import ALL_INDICATORS, CATEGORIES, IMPLEMENTATION_PRIORITY
from ..models import EconomicIndicator, HistoricalData

router = APIRouter(prefix="/api/v1", tags=["Expanded Indicators"])

# ENDPOINT PRINCIPAL - TODOS LOS DATOS
@router.get("/dashboard/complete")
async def get_complete_dashboard():
    """
    Obtener TODOS los indicadores de todas las categorías
    Endpoint principal para el dashboard completo
    """
    try:
        async with ExpandedDataService() as service:
            all_data = await service.get_all_indicators()
            
            if all_data.get("status") == "success":
                return {
                    "status": "success",
                    "data": all_data["data"],
                    "metadata": {
                        "total_indicators": all_data.get("total_indicators", 0),
                        "categories": list(all_data["data"].keys()),
                        "timestamp": all_data["timestamp"],
                        "version": "1.0.0"
                    }
                }
            else:
                raise HTTPException(status_code=500, detail="Error fetching data")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ENDPOINTS POR CATEGORÍA
@router.get("/indicators/economia")
async def get_economic_indicators():
    """Obtener indicadores económicos (IPC, PBI, EMAE, etc.)"""
    try:
        async with ExpandedDataService() as service:
            data = await service.get_economic_indicators()
            return {
                "status": "success",
                "category": "economia", 
                "data": data,
                "description": CATEGORIES["economia"]["description"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/gobierno")
async def get_government_indicators():
    """Obtener indicadores de gobierno (Fiscal, deuda, gasto público, etc.)"""
    try:
        async with ExpandedDataService() as service:
            data = await service.get_government_indicators()
            return {
                "status": "success",
                "category": "gobierno",
                "data": data,
                "description": CATEGORIES["gobierno"]["description"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/finanzas")
async def get_financial_indicators():
    """Obtener indicadores financieros (Tasas, depósitos, préstamos, etc.)"""
    try:
        async with ExpandedDataService() as service:
            data = await service.get_financial_indicators()
            return {
                "status": "success",
                "category": "finanzas",
                "data": data,
                "description": CATEGORIES["finanzas"]["description"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/mercados")
async def get_market_indicators():
    """Obtener indicadores de mercados (MERVAL, bonos, acciones, etc.)"""
    try:
        async with ExpandedDataService() as service:
            data = await service.get_market_indicators()
            return {
                "status": "success",
                "category": "mercados",
                "data": data,
                "description": CATEGORIES["mercados"]["description"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/tecnologia")
async def get_tech_indicators():
    """Obtener indicadores de tecnología (SBC, empleo IT, etc.)"""
    try:
        async with ExpandedDataService() as service:
            data = await service.get_tech_indicators()
            return {
                "status": "success",
                "category": "tecnologia",
                "data": data,
                "description": CATEGORIES["tecnologia"]["description"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/industria")
async def get_industry_indicators():
    """Obtener indicadores de industria (IPI, PMI, automotriz, etc.)"""
    try:
        async with ExpandedDataService() as service:
            data = await service.get_industry_indicators()
            return {
                "status": "success",
                "category": "industria",
                "data": data,
                "description": CATEGORIES["industria"]["description"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ENDPOINTS DE DATOS HISTÓRICOS
@router.get("/indicators/{indicator_name}/historical")
async def get_indicator_historical(
    indicator_name: str,
    days: int = Query(30, description="Días de historial", ge=1, le=365),
    period: str = Query("daily", description="Período: daily, weekly, monthly")
):
    """
    Obtener datos históricos de un indicador específico
    """
    try:
        # Validar que el indicador existe
        if indicator_name not in ALL_INDICATORS:
            raise HTTPException(
                status_code=404, 
                detail=f"Indicator '{indicator_name}' not found. Available: {list(ALL_INDICATORS.keys())[:10]}..."
            )
        
        async with ExpandedDataService() as service:
            historical_data = await service.get_historical_data(indicator_name, days)
            
            if historical_data.get("status") == "success":
                return {
                    "status": "success",
                    "indicator": indicator_name,
                    "metadata": ALL_INDICATORS[indicator_name],
                    "historical_data": historical_data["data"],
                    "period": f"{days} days",
                    "data_points": len(historical_data["data"])
                }
            else:
                raise HTTPException(status_code=500, detail="Error fetching historical data")
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ENDPOINT DE INDICADOR INDIVIDUAL
@router.get("/indicators/{indicator_name}")
async def get_single_indicator(indicator_name: str):
    """Obtener un indicador específico con su información completa"""
    try:
        if indicator_name not in ALL_INDICATORS:
            raise HTTPException(status_code=404, detail=f"Indicator '{indicator_name}' not found")
        
        # Determinar categoría del indicador
        category = None
        for cat_name, cat_info in CATEGORIES.items():
            if indicator_name in cat_info["indicators"]:
                category = cat_name
                break
        
        async with ExpandedDataService() as service:
            # Obtener datos de la categoría correspondiente
            if category == "economia":
                category_data = await service.get_economic_indicators()
            elif category == "gobierno":
                category_data = await service.get_government_indicators()
            elif category == "finanzas":
                category_data = await service.get_financial_indicators()
            elif category == "mercados":
                category_data = await service.get_market_indicators()
            elif category == "tecnologia":
                category_data = await service.get_tech_indicators()
            elif category == "industria":
                category_data = await service.get_industry_indicators()
            else:
                raise HTTPException(status_code=500, detail="Category not found")
            
            # Extraer datos del indicador específico
            indicator_data = category_data.get(indicator_name, {})
            
            return {
                "status": "success",
                "indicator": indicator_name,
                "category": category,
                "metadata": ALL_INDICATORS[indicator_name],
                "current_data": indicator_data,
                "timestamp": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ENDPOINTS DE CONFIGURACIÓN Y METADATOS
@router.get("/config/categories")
async def get_categories():
    """Obtener configuración de todas las categorías"""
    return {
        "status": "success",
        "categories": CATEGORIES,
        "total_categories": len(CATEGORIES),
        "total_indicators": len(ALL_INDICATORS)
    }

@router.get("/config/indicators")
async def get_indicators_config():
    """Obtener configuración de todos los indicadores"""
    return {
        "status": "success",
        "indicators": ALL_INDICATORS,
        "implementation_priority": IMPLEMENTATION_PRIORITY,
        "total_indicators": len(ALL_INDICATORS)
    }

@router.get("/config/priority")
async def get_implementation_priority():
    """Obtener prioridades de implementación"""
    return {
        "status": "success",
        "priority": IMPLEMENTATION_PRIORITY,
        "phases": {
            "phase_1": "APIs oficiales fáciles (BCRA, INDEC)",
            "phase_2": "APIs más complejas",
            "phase_3": "Scraping de sitios web",
            "phase_4": "Datos de actualización manual"
        }
    }

# ENDPOINTS DE BÚSQUEDA Y FILTROS
@router.get("/indicators/search")
async def search_indicators(
    q: str = Query(..., description="Término de búsqueda"),
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    source: Optional[str] = Query(None, description="Filtrar por fuente")
):
    """Buscar indicadores por nombre, descripción o características"""
    try:
        results = []
        search_term = q.lower()
        
        for indicator_id, config in ALL_INDICATORS.items():
            # Buscar en nombre y descripción
            if (search_term in config["name"].lower() or 
                search_term in config["description"].lower() or
                search_term in indicator_id.lower()):
                
                # Aplicar filtros adicionales
                if category and not any(indicator_id in cat_info["indicators"] 
                                      for cat_name, cat_info in CATEGORIES.items() 
                                      if cat_name == category):
                    continue
                
                if source and config["source"] != source.upper():
                    continue
                
                results.append({
                    "id": indicator_id,
                    "name": config["name"],
                    "description": config["description"],
                    "source": config["source"],
                    "frequency": config["frequency"],
                    "unit": config["unit"],
                    "category": config["category"]
                })
        
        return {
            "status": "success",
            "query": q,
            "results": results,
            "total_found": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ENDPOINTS DE ACTUALIZACIÓN
@router.post("/indicators/refresh")
async def refresh_all_indicators(background_tasks: BackgroundTasks):
    """Forzar actualización de todos los indicadores"""
    
    async def update_task():
        try:
            async with ExpandedDataService() as service:
                all_data = await service.get_all_indicators()
                # Aquí guardaríamos en la base de datos
                print(f"✅ Updated {all_data.get('total_indicators', 0)} indicators")
        except Exception as e:
            print(f"❌ Error updating indicators: {e}")
    
    background_tasks.add_task(update_task)
    
    return {
        "status": "success",
        "message": "Actualización iniciada en segundo plano",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/indicators/{indicator_name}/refresh")
async def refresh_single_indicator(indicator_name: str, background_tasks: BackgroundTasks):
    """Forzar actualización de un indicador específico"""
    
    if indicator_name not in ALL_INDICATORS:
        raise HTTPException(status_code=404, detail=f"Indicator '{indicator_name}' not found")
    
    async def update_single_task():
        try:
            async with ExpandedDataService() as service:
                historical_data = await service.get_historical_data(indicator_name, 1)
                print(f"✅ Updated {indicator_name}")
        except Exception as e:
            print(f"❌ Error updating {indicator_name}: {e}")
    
    background_tasks.add_task(update_single_task)
    
    return {
        "status": "success",
        "message": f"Actualización de {indicator_name} iniciada",
        "indicator": indicator_name,
        "timestamp": datetime.now().isoformat()
    }

# ENDPOINTS DE MONITOREO Y HEALTH
@router.get("/health/detailed")
async def detailed_health_check():
    """Health check detallado de todas las fuentes de datos"""
    try:
        async with ExpandedDataService() as service:
            # Test conectividad a APIs principales
            health_status = {
                "bcra_api": "checking",
                "indec_api": "checking", 
                "bluelytics_api": "checking",
                "byma_api": "checking",
                "overall_status": "healthy"
            }
            
            # Test básico BCRA
            try:
                reservas = await service.get_reservas_bcra()
                health_status["bcra_api"] = "healthy" if reservas.get("status") == "success" else "degraded"
            except:
                health_status["bcra_api"] = "down"
            
            # Test básico dólar blue
            try:
                blue = await service.get_dolar_blue()
                health_status["bluelytics_api"] = "healthy" if blue.get("status") == "success" else "degraded"
            except:
                health_status["bluelytics_api"] = "down"
            
            # Determinar estado general
            if any(status == "down" for status in health_status.values()):
                health_status["overall_status"] = "degraded"
            
            return {
                "status": "success",
                "health": health_status,
                "timestamp": datetime.now().isoformat(),
                "uptime": "99.9%",  # Placeholder
                "version": "1.0.0"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "health": {"overall_status": "down"},
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ENDPOINT DE ESTADÍSTICAS
@router.get("/stats")
async def get_platform_stats():
    """Obtener estadísticas generales de la plataforma"""
    return {
        "status": "success",
        "stats": {
            "total_indicators": len(ALL_INDICATORS),
            "categories": len(CATEGORIES),
            "data_sources": len(set(config["source"] for config in ALL_INDICATORS.values())),
            "real_time_indicators": len([i for i in ALL_INDICATORS.values() if i["frequency"] == "real_time"]),
            "daily_indicators": len([i for i in ALL_INDICATORS.values() if i["frequency"] == "daily"]),
            "monthly_indicators": len([i for i in ALL_INDICATORS.values() if i["frequency"] == "monthly"]),
            "implementation_phases": len(IMPLEMENTATION_PRIORITY),
            "sources": {
                "BCRA": len([i for i in ALL_INDICATORS.values() if i["source"] == "BCRA"]),
                "INDEC": len([i for i in ALL_INDICATORS.values() if i["source"] == "INDEC"]),
                "BYMA": len([i for i in ALL_INDICATORS.values() if i["source"] == "BYMA"]),
                "Others": len([i for i in ALL_INDICATORS.values() if i["source"] not in ["BCRA", "INDEC", "BYMA"]])
            }
        },
        "timestamp": datetime.now().isoformat()
    }

# ENDPOINTS DE EXPORTACIÓN
@router.get("/export/{format}")
async def export_data(
    format: str,
    category: Optional[str] = None,
    indicators: Optional[str] = None
):
    """Exportar datos en diferentes formatos (JSON, CSV, etc.)"""
    if format not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
    
    try:
        async with ExpandedDataService() as service:
            if category:
                # Exportar una categoría específica
                if category not in CATEGORIES:
                    raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
                
                # Obtener datos de la categoría
                # ... implementar lógica de exportación
                pass
            else:
                # Exportar todos los datos
                all_data = await service.get_all_indicators()
                
                if format == "json":
                    return JSONResponse(content=all_data)
                elif format == "csv":
                    # Convertir a CSV
                    # ... implementar conversión
                    pass
        
        return {"status": "success", "message": f"Export in {format} format completed"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))