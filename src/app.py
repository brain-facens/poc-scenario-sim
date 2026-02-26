import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utilities import repeat_every

from database import SessionLocal
from routes import general_routes, users_routes, simulation_routes
from services.simulation_services import cleanup_timed_out_simulations, process_stale_queue

@repeat_every(seconds=60)
async def simulation_watchdog():
    print("DEBUG: Watchdog cycle started...")
    """Periodically checks for timeouts and processes the queue."""
    db = SessionLocal()
    try:
        cleanup_count = cleanup_timed_out_simulations(db)
        promoted_id = await process_stale_queue(db)
        
        if cleanup_count > 0 or promoted_id:
            print(f"Watchdog: Cleaned {cleanup_count} | Promoted {promoted_id}")
            
    except Exception as e:
        print(f"Watchdog Error: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await simulation_watchdog()
    yield

app = FastAPI(title="sql alchemy", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(general_routes.general_router)
app.include_router(users_routes.users_router)
app.include_router(simulation_routes.simulation_router)

if __name__ == "__main__":
    uvicorn.run("app:app", reload=True, timeout_keep_alive=120)