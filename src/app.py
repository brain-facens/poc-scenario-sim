from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utilities import repeat_every

from database import SessionLocal

# --- Module routers ---
from modules.auth.routes.user_routes import users_router
from modules.general.routes.general_routes import general_router
from modules.gerador_atas.routes.ata_routes import atas_router
from modules.scenario_sim.routes.actor_routes import actor_router
from modules.scenario_sim.routes.material_routes import material_router
from modules.scenario_sim.routes.scene_routes import scene_router
from modules.scenario_sim.routes.simulation_routes import simulation_router
from modules.scenario_sim.services.simulation_services import (
    cleanup_timed_out_simulations,
    process_stale_queue,
)


@repeat_every(seconds=900)
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


app = FastAPI(title="Brain Hub API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# General
app.include_router(general_router)

# Auth / Users
app.include_router(users_router)

# Scenario Simulation
app.include_router(simulation_router)
app.include_router(actor_router)
app.include_router(scene_router)
app.include_router(material_router)

# Gerador de ATAs
app.include_router(atas_router)

if __name__ == "__main__":
    uvicorn.run("app:app", reload=True, timeout_keep_alive=120)
