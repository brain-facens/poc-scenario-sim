from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.simulation_input_schemas import SimulationFullRead, SimulationInputCreate, SimulationInputRead
from services.simulation_services import create_simulation_input_service, get_simulations_by_input_id_service

simulation_router = APIRouter(prefix="/simulations", tags=["simulations"])

@simulation_router.post("/", response_model=SimulationInputRead, status_code=status.HTTP_201_CREATED)
async def create_simulation_input(
    simulation_input: SimulationInputCreate, 
    db: Session = Depends(get_db)
):
    """
    Creates a new SimulationInput record in the database using the provided pitch.
    """
    return await create_simulation_input_service(db=db, input_data=simulation_input)

@simulation_router.get("/{input_id}", response_model=List[SimulationFullRead])
def get_simulations_by_input(input_id: str, db: Session = Depends(get_db)):
    """
    Returns a full nested visualization of all simulations 
    linked to the provided SimulationInput ID.
    """
    return get_simulations_by_input_id_service(db, simulation_input_id=input_id)