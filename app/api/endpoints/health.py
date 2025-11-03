from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/", tags=["Health Check"])
async def health_check():
    return {"status": "HEALTHY", "current_time": datetime.utcnow().isoformat() + "Z"}
