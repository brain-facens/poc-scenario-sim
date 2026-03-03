from fastapi import APIRouter, Depends, Request, HTTPException

from database import engine, Base

general_router = APIRouter(prefix="/general", tags=["general"])
@general_router.get("/status")
async def get_status(request: Request):
    return {"status": "ok"}

@general_router.delete("/clear_local")
async def clear_data():
    try:
        metadata = Base.metadata
        
        with engine.begin() as connection:
            for table in reversed(metadata.sorted_tables):
                connection.execute(table.delete())
        
        return {"message": "All data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))