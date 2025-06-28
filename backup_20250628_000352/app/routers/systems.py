import platform
from datetime import datetime
from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/info", summary="Info del sistema host")
async def system_info():
    return {
        "python": platform.python_version(),
        "os": platform.system(),
        "machine": platform.machine(),
        "timestamp": datetime.utcnow().isoformat(),
    }