from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.simulation_input_schemas import SimulationInputCreate, SimulationInputRead
from services.simulation_services import create_simulation_input_service

simulation_router = APIRouter(prefix="/simulations", tags=["simulations"])

@simulation_router.post("/", response_model=SimulationInputRead, status_code=status.HTTP_201_CREATED)
def create_simulation_input(
    simulation_input: SimulationInputCreate, 
    db: Session = Depends(get_db)
):
    """
    Creates a new SimulationInput record in the database using the provided pitch.
    """
    return create_simulation_input_service(db=db, input_data=simulation_input)