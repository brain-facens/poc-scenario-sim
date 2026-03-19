from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from database import get_db
from modules.scenario_sim.schemas.simulation_schemas import (
    SimulationFullRead,
    SimulationInputCreate,
    SimulationInputRead,
    SimulationUpdateSchema,
)
from modules.scenario_sim.services.simulation_services import (
    create_simulation_input_service,
    generate_and_save_pdf_service,
    get_all_simulation_ids_service,
    get_simulation_by_id_service,
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


@simulation_router.post("/{simulation_id}/pdf")
async def trigger_pdf_generation(
    simulation_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Triggers the generation of a new PDF for a specific simulation in the background.
    """
    success = await generate_and_save_pdf_service(
        db, simulation_id=simulation_id, background_tasks=background_tasks
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )

    return {"message": "PDF generation started"}


@simulation_router.get("/pdf/{simulation_id}", response_class=FileResponse)
async def fetch_simulation_pdf(simulation_id: str, db: Session = Depends(get_db)):
    """
    Returns the EXISTING PDF file for a specific simulation without regenerating it.
    """
    simulation = get_simulation_by_id_service(db, simulation_id=simulation_id)
    if not simulation or not simulation.pdf_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PDF not found for this simulation"
        )

    return FileResponse(
        path=str(simulation.pdf_path),
        filename=f"simulation_{simulation_id}.pdf",
        media_type="application/pdf",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@simulation_router.get("/", response_model=List[SimulationFullRead])
def list_simulations(db: Session = Depends(get_db)):
    """
    Returns a list of all simulations in the database.
    """
    return get_all_simulation_ids_service(db)


@simulation_router.get("/{input_id}", response_model=List[SimulationFullRead])
def get_simulations_by_input(input_id: str, db: Session = Depends(get_db)):
    """
    Returns a full nested visualization of all simulations
    linked to the provided SimulationInput ID.
    """
    return get_simulations_by_input_id_service(db, simulation_input_id=input_id)


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
