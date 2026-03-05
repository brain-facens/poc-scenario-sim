from fastapi import APIRouter, Depends, Request, HTTPException

from services.general_services import clear_all_data

general_router = APIRouter(prefix="/general", tags=["general"])
@general_router.get("/status")
async def get_status(request: Request):
    return {"status": "ok"}

@general_router.delete("/clear_local")
async def clear_data():
    try:
        clear_all_data()        
        return {"message": "All data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))