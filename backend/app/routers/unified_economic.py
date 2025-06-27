# backend/app/routers/unified_economic.py
# Router limpio sin problemas de f-string
from fastapi import APIRouter, HTTPException
from datetime import datetime
from ..services.unified_service import unified_service
from ..services.http_factory import HTTPClientFactory

router = APIRouter(prefix="/api/v1/unified", tags=["Unified Economic Data"])

@router.get("/capabilities")
async def get_http_capabilities():
    """Ver que librerias HTTP estan disponibles"""
    caps = HTTPClientFactory.get_capabilities()
    return {
        "capabilities": caps,
        "recommendation": {
            "scraping": "requests" if caps["requests"] else "none",
            "modern_api": "httpx" if caps["httpx"] else "requests",
            "massive_parallel": "aiohttp" if caps["aiohttp"] else "httpx" if caps["httpx"] else "requests"
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/dollar")
async def get_unified_dollar():
    """Obtener dolar usando todas las fuentes disponibles"""
    try:
        result = await unified_service.get_dollar_data()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/massive-bcra")
async def get_massive_bcra():
    """Obtener datos masivos BCRA usando la mejor estrategia"""
    try:
        result = await unified_service.get_massive_bcra_data()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-all")
async def test_all_services():
    """Test todos los servicios disponibles"""
    results = {}
    
    # Test capacidades
    caps = HTTPClientFactory.get_capabilities()
    results["capabilities"] = caps
    
    # Test httpx
    if caps.get("httpx"):
        try:
            from ..services.modern.bcra_httpx_service import bcra_httpx_service
            async with bcra_httpx_service as service:
                httpx_result = await service.get_exchange_rates()
                results["httpx"] = "OK" if httpx_result.get("status") == "success" else "FAIL"
        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 50:
                error_msg = error_msg[:50] + "..."
            results["httpx"] = "ERROR: " + error_msg
    else:
        results["httpx"] = "NOT_AVAILABLE"
    
    # Test aiohttp
    if caps.get("aiohttp"):
        try:
            results["aiohttp"] = "AVAILABLE"
        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 50:
                error_msg = error_msg[:50] + "..."
            results["aiohttp"] = "ERROR: " + error_msg
    else:
        results["aiohttp"] = "NOT_AVAILABLE"
    
    return {
        "test_results": results,
        "capabilities": caps,
        "timestamp": datetime.now().isoformat()
    }
