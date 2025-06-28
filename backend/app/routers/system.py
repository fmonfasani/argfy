# System router implementationfrom datetime import datetime
import platform
from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/info", summary="Información básica del host")
async def system_info():
    return {
        "python": platform.python_version(),
        "os": platform.system(),
        "machine": platform.machine(),
        "timestamp": datetime.utcnow().isoformat(),
    }