from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
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
from modules.scenario_sim.routes.evaluation_routes import evaluation_router
from modules.scenario_sim.services.simulation_services import (
    cleanup_timed_out_simulations,
    process_stale_queue,
)
from modules.gerador_atas.services.ata_services import (
    cleanup_timed_out_atas,
    process_stale_ata_queue,
)
from modules.logging.middleware.request_logging_middleware import RequestLoggingMiddleware
from modules.logging.routes.request_log_routes import logs_router
from modules.voice_changer.routes.voice_changer_routes import voice_changer_router
from modules.voice_changer.services.voice_changer_services import check_health


@repeat_every(seconds=5)
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


@repeat_every(seconds=5)
async def ata_watchdog():
    print("DEBUG: Ata Watchdog cycle started...")
    """Periodically checks for timeouts and processes the ATA queue."""
    db = SessionLocal()
    try:
        cleanup_count = cleanup_timed_out_atas(db)
        promoted_id = await process_stale_ata_queue(db)

        if cleanup_count > 0 or promoted_id:
            print(f"Ata Watchdog: Cleaned {cleanup_count} | Promoted {promoted_id}")

    except Exception as e:
        print(f"Ata Watchdog Error: {e}")
    finally:
        db.close()



@repeat_every(seconds=870)
async def keep_voice_changer_alive():
    """Pings the Voice Changer API to prevent it from sleeping on Render."""
    try:
        result = await run_in_threadpool(check_health)
        print(f"Voice Changer ping successful: {result}")
    except Exception as e:
        print(f"Voice Changer ping failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await simulation_watchdog()
    await ata_watchdog()
    await keep_voice_changer_alive()
    yield


app = FastAPI(title="Brain Hub API", lifespan=lifespan)

# --- Middleware (order matters: last added = outermost) ---
app.add_middleware(RequestLoggingMiddleware)

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
app.include_router(evaluation_router)

# Gerador de ATAs
app.include_router(atas_router)

# Voice Changer
app.include_router(voice_changer_router)

# Logging
app.include_router(logs_router)

if __name__ == "__main__":
    uvicorn.run("app:app", reload=True, timeout_keep_alive=86400)
