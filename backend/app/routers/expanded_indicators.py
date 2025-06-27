# backend/app/routers/expanded_indicators.py
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import EconomicIndicator, HistoricalData, NewsItem
from ..services.bcra_expanded_service import BCRAExpandedService
from ..services.dollar_multi_source import DollarMultiSourceService
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import asyncio

router = APIRouter(prefix="/expanded", tags=["Expanded Economic Data"])

@router.get("/dashboard/complete")
async def get_complete_dashboard():
    """Dashboard COMPLETO con todos los datos económicos disponibles"""
    try:
        # Ejecutar servicios en paralelo para máxima velocidad
        async with BCRAExpandedService() as bcra_service:
            async with DollarMultiSourceService() as dollar_service:
                
                # Tareas en paralelo
                tasks = [
                    bcra_service.get_complete_dashboard(),
                    dollar_service.get_all_dollar_rates(),
                    dollar_service.get_blue_dollar_consensus()
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                bcra_data = results[0] if not isinstance(results[0], Exception) else {}
                dollar_data = results[1] if not isinstance(results[1], Exception) else {}
                blue_consensus = results[2] if not isinstance(results[2], Exception) else {}
                
                # Consolidar dashboard completo
                complete_dashboard = {
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "data_sources": ["BCRA_EXPANDED", "MULTI_DOLLAR_APIs", "CONSENSUS_BLUE"],
                    "summary": {
                        "total_bcra_indicators": 0,
                        "total_currencies": 0,
                        "dollar_sources": 0,
                        "blue_dollar_consensus": None,
                        "data_freshness": "real_time"
                    },
                    "bcra_data": {},
                    "dollar_rates": {},
                    "blue_dollar": {},
                    "reliability_scores": {}
                }
                
                # Procesar datos BCRA
                if bcra_data.get("status") == "success":
                    complete_dashboard["bcra_data"] = bcra_data
                    summary = bcra_data.get("summary", {})
                    complete_dashboard["summary"]["total_bcra_indicators"] = summary.get("total_indicators", 0)
                    complete_dashboard["summary"]["total_currencies"] = summary.get("total_currencies", 0)
                    complete_dashboard["reliability_scores"]["bcra"] = 1.0
                else:
                    complete_dashboard["reliability_scores"]["bcra"] = 0.0
                
                # Procesar datos de dólar
                if dollar_data.get("status") == "success":
                    complete_dashboard["dollar_rates"] = dollar_data.get("data", {})
                    complete_dashboard["summary"]["dollar_sources"] = dollar_data.get("sources_used", 0)
                    complete_dashboard["reliability_scores"]["dollar_apis"] = dollar_data.get("reliability_score", 0)
                
                # Procesar consenso blue
                if blue_consensus.get("status") == "success":
                    complete_dashboard["blue_dollar"] = blue_consensus.get("blue_dollar", {})
                    complete_dashboard["summary"]["blue_dollar_consensus"] = blue_consensus.get("blue_dollar", {}).get("average")
                    complete_dashboard["reliability_scores"]["blue_consensus"] = 1.0 if blue_consensus.get("reliability") == "high" else 0.8
                
                # Calcular score general de confiabilidad
                reliability_scores = complete_dashboard["reliability_scores"]
                overall_reliability = sum(reliability_scores.values()) / len(reliability_scores) if reliability_scores else 0
                complete_dashboard["summary"]["overall_reliability"] = round(overall_reliability, 2)
                
                return complete_dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting complete dashboard: {str(e)}")

@router.get("/bcra/all")
async def get_all_bcra_data():
    """Obtener TODAS las variables disponibles del BCRA"""
    try:
        async with BCRAExpandedService() as service:
            result = await service.get_complete_dashboard()
            
            if result.get("status") == "success":
                return {
                    "status": "success",
                    "data": result,
                    "timestamp": datetime.now().isoformat(),
                    "total_indicators": result.get("summary", {}).get("total_indicators", 0),
                    "categories": [
                        "monetary_indicators", "interest_rates", "exchange_rates",
                        "deposits_loans", "external_sector", "inflation_data"
                    ]
                }
            else:
                raise HTTPException(status_code=500, detail="Error fetching BCRA data")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/bcra/category/{category}")
async def get_bcra_by_category(category: str):
    """Obtener indicadores BCRA por categoría específica"""
    try:
        valid_categories = [
            "monetary_indicators", "interest_rates", "exchange_rates",
            "deposits_loans", "external_sector", "inflation_data"
        ]
        
        if category not in valid_categories:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid category. Valid options: {valid_categories}"
            )
        
        async with BCRAExpandedService() as service:
            dashboard = await service.get_complete_dashboard()
            
            if dashboard.get("status") == "success":
                category_data = dashboard.get(category, {})
                
                return {
                    "status": "success",
                    "category": category,
                    "data": category_data,
                    "count": len(category_data),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise HTTPException(status_code=500, detail="Error fetching BCRA data")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/dollar/all-types")
async def get_all_dollar_types():
    """Obtener todos los tipos de dólar de múltiples fuentes"""
    try:
        async with DollarMultiSourceService() as service:
            result = await service.get_all_dollar_rates()
            
            return {
                "status": result.get("status"),
                "data": result.get("data", {}),
                "sources_info": {
                    "sources_used": result.get("sources_used", 0),
                    "total_sources": result.get("total_sources", 0),
                    "reliability_score": result.get("reliability_score", 0)
                },
                "timestamp": result.get("timestamp")
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/dollar/blue/consensus")
async def get_blue_dollar_consensus():
    """Obtener consenso del dólar blue entre múltiples fuentes"""
    try:
        async with DollarMultiSourceService() as service:
            result = await service.get_blue_dollar_consensus()
            
            if result.get("status") == "success":
                return {
                    "status": "success",
                    "blue_dollar": result.get("blue_dollar"),
                    "reliability": result.get("reliability"),
                    "timestamp": result.get("timestamp"),
                    "analysis": {
                        "recommendation": "buy" if result.get("blue_dollar", {}).get("spread_percent", 0) < 2 else "wait",
                        "market_stability": "stable" if result.get("blue_dollar", {}).get("spread_percent", 0) < 3 else "volatile"
                    }
                }
            else:
                raise HTTPException(status_code=500, detail=result.get("message", "Error fetching blue dollar data"))
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/currencies/all")
async def get_all_currencies():
    """Obtener TODAS las cotizaciones de monedas del BCRA"""
    try:
        async with BCRAExpandedService() as service:
            result = await service.get_all_cotizaciones()
            
            if result.get("status") == "success":
                cotizaciones = result.get("cotizaciones", {})
                
                # Separar por categorías
                categorized = {
                    "major": {},
                    "regional": {},
                    "asian": {},
                    "european": {},
                    "emerging": {},
                    "other": {}
                }
                
                for code, data in cotizaciones.items():
                    category = data.get("category", "other")
                    categorized[category][code] = data
                
                return {
                    "status": "success",
                    "data": {
                        "all_currencies": cotizaciones,
                        "by_category": categorized
                    },
                    "summary": {
                        "total_currencies": result.get("total_currencies", 0),
                        "major_currencies": result.get("major_currencies", 0),
                        "update_date": result.get("date")
                    },
                    "timestamp": result.get("timestamp")
                }
            else:
                raise HTTPException(status_code=500, detail="Error fetching currencies")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/data/refresh")
async def refresh_all_data(background_tasks: BackgroundTasks):
    """Actualizar TODOS los datos de todas las fuentes"""
    
    async def refresh_task():
        try:
            # Actualizar BCRA
            async with BCRAExpandedService() as bcra_service:
                dashboard_data = await bcra_service.get_complete_dashboard()
                if dashboard_data.get("status") == "success":
                    await bcra_service.save_expanded_data(dashboard_data)
            
            # Actualizar datos de dólar (no necesita guardarse, son en tiempo real)
            async with DollarMultiSourceService() as dollar_service:
                await dollar_service.get_all_dollar_rates()
            
            print(f"✅ Datos actualizados: {datetime.now()}")
            
        except Exception as e:
            print(f"❌ Error en actualización: {e}")
    
    background_tasks.add_task(refresh_task)
    
    return {
        "status": "success",
        "message": "Actualización de todos los datos iniciada en segundo plano",
        "timestamp": datetime.now().isoformat(),
        "estimated_completion": (datetime.now() + timedelta(minutes=2)).isoformat()
    }

@router.get("/data/status")
async def get_data_status():
    """Obtener estado actual de todas las fuentes de datos"""
    try:
        status_report = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "overall_status": "operational"
        }
        
        # Test BCRA
        try:
            async with BCRAExpandedService() as bcra_service:
                bcra_test = await bcra_service.get_all_bcra_variables()
                status_report["services"]["bcra"] = {
                    "status": "operational" if bcra_test.get("status") == "success" else "degraded",
                    "total_variables": bcra_test.get("total_variables", 0),
                    "last_check": datetime.now().isoformat()
                }
        except Exception as e:
            status_report["services"]["bcra"] = {
                "status": "down",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
        
        # Test Dollar APIs
        try:
            async with DollarMultiSourceService() as dollar_service:
                dollar_test = await dollar_service.get_all_dollar_rates()
                status_report["services"]["dollar_apis"] = {
                    "status": "operational" if dollar_test.get("status") == "success" else "degraded",
                    "sources_working": dollar_test.get("sources_used", 0),
                    "total_sources": dollar_test.get("total_sources", 0),
                    "reliability": dollar_test.get("reliability_score", 0),
                    "last_check": datetime.now().isoformat()
                }
        except Exception as e:
            status_report["services"]["dollar_apis"] = {
                "status": "down",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
        
        # Determinar estado general
        service_statuses = [service.get("status") for service in status_report["services"].values()]
        if all(status == "operational" for status in service_statuses):
            status_report["overall_status"] = "operational"
        elif any(status == "operational" for status in service_statuses):
            status_report["overall_status"] = "degraded"
        else:
            status_report["overall_status"] = "down"
        
        return status_report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking status: {str(e)}")

@router.get("/summary/quick")
async def get_quick_summary():
    """Resumen rápido de indicadores clave para dashboards"""
    try:
        summary = {}
        
        async with BCRAExpandedService() as bcra_service:
            async with DollarMultiSourceService() as dollar_service:
                
                # Tareas en paralelo para velocidad
                tasks = [
                    bcra_service.get_all_bcra_variables(),
                    dollar_service.get_blue_dollar_consensus()
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                bcra_vars = results[0] if not isinstance(results[0], Exception) else {}
                blue_consensus = results[1] if not isinstance(results[1], Exception) else {}
                
                # Extraer indicadores clave
                if bcra_vars.get("status") == "success":
                    vars_data = bcra_vars.get("variables", {})
                    
                    # Indicadores principales
                    key_indicators = {}
                    for key, data in vars_data.items():
                        if key in ["usd_mayorista", "reservas_internacionales", "tasa_politica_nominal", "inflacion_mensual"]:
                            key_indicators[key] = {
                                "value": data["value"],
                                "label": data["label"],
                                "unit": data["unit"],
                                "date": data["date"]
                            }
                    
                    summary["bcra_key_indicators"] = key_indicators
                
                # Dólar blue
                if blue_consensus.get("status") == "success":
                    blue_data = blue_consensus.get("blue_dollar", {})
                    summary["blue_dollar"] = {
                        "price": blue_data.get("average"),
                        "spread": blue_data.get("spread"),
                        "reliability": blue_consensus.get("reliability"),
                        "sources": blue_data.get("sources_count")
                    }
                
                summary["timestamp"] = datetime.now().isoformat()
                summary["status"] = "success"
                
                return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting quick summary: {str(e)}")