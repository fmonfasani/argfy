from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/ping", summary="Simple ping-pong")
async def ping():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}