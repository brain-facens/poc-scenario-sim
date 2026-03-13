import io
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from database import get_db
from models.simulation_model import Simulation
from schemas.simulation_input_schemas import (
    SimulationFullRead,
    SimulationInputCreate,
    SimulationInputRead,
    SimulationUpdateSchema,
)
from services.simulation_services import (
    create_simulation_input_service,
    generate_pdf,
    get_all_simulation_ids_service,
    get_simulations_by_input_id_service,
    update_simulation_service,
)

simulation_router = APIRouter(prefix="/simulations", tags=["simulations"])


@simulation_router.post(
    "/", response_model=SimulationInputRead, status_code=status.HTTP_201_CREATED
)
async def create_simulation_input(
    simulation_input: SimulationInputCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Creates a new SimulationInput record in the database using the provided pitch.
    """
    return await create_simulation_input_service(
        db=db, input_data=simulation_input, background_tasks=background_tasks
    )


@simulation_router.get("/{input_id}", response_model=List[SimulationFullRead])
def get_simulations_by_input(input_id: str, db: Session = Depends(get_db)):
    """
    Returns a full nested visualization of all simulations
    linked to the provided SimulationInput ID.
    """
    return get_simulations_by_input_id_service(db, simulation_input_id=input_id)


@simulation_router.get("/pdf/{input_id}", response_model=bytes)
async def generate_simulation_pdf(input_id: str, db: Session = Depends(get_db)):
    """
    Generates a PDF file for the simulation associated with the provided input ID.
    """
    simulations = get_simulations_by_input_id_service(db, simulation_input_id=input_id)
    if not simulations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found"
        )

    sim_data: Simulation = simulations[0]
    # pdf_path: str = await generate_pdf(sim_data)
    return FileResponse(
        path=str(sim_data.pdf_path),
        filename="simulation.pdf",
        media_type="application/pdf",
    )


@simulation_router.get("/", response_model=List[SimulationFullRead])
def list_simulations(db: Session = Depends(get_db)):
    """
    Returns a list of all simulations in the database.
    """
    return get_all_simulation_ids_service(db)


@simulation_router.patch("/{simulation_id}", response_model=SimulationFullRead)
def update_simulation(
    simulation_id: str,
    update_data: SimulationUpdateSchema,
    db: Session = Depends(get_db),
):
    """
    Updates specific fields of an existing simulation.
    """
    updated_sim = update_simulation_service(db, simulation_id, update_data)
    if not updated_sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return updated_sim
