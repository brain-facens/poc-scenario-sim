from sqlalchemy.orm import Session
from models import SimulationInput, Simulation
from schemas.simulation_input_schemas import SimulationInputCreate

def create_simulation_input_service(db: Session, input_data: SimulationInputCreate):
    """
    Creates a new SimulationInput record in the database.
    """
    db_input = SimulationInput(
        pitch=input_data.pitch
    )
    
    db.add(db_input)
    db.commit()
    db.refresh(db_input)
    
    print(f"DB INPUT: {db_input}")
    
    return db_input