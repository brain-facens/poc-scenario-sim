from fastapi import APIRouter, Depends, Request, HTTPException

general_router = APIRouter(prefix="/general", tags=["general"])
@general_router.get("/status")
async def get_status(request: Request):
    return {"status": "ok"}