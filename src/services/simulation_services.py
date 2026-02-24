import asyncio
import traceback

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from gen_tests.gen_parts.scenario import Scenario
from gen_tests.gen_sim import generate
from models import Actor, Material, Scene, Simulation, SimulationInput
from models.simulation_model import SimulationStatus
from schemas.simulation_input_schemas import SimulationInputCreate


async def create_simulation_input_service(db: Session, input_data: SimulationInputCreate, background_tasks: BackgroundTasks):
    db_input = SimulationInput(pitch=input_data.pitch)
    db.add(db_input)
    db.commit()
    db.refresh(db_input)

    active_exists = db.query(Simulation).filter(
        Simulation.status == SimulationStatus.DOING
    ).first() is not None

    initial_status = SimulationStatus.STALE if active_exists else SimulationStatus.DOING

    new_simulation = Simulation(
        simulation_input_id=db_input.id,
        status=initial_status
    )
    db.add(new_simulation)
    db.commit()

    if initial_status == SimulationStatus.DOING:
        background_tasks.add_task(run_simulation_generation_task, db_input.id, new_simulation.id, input_data.pitch)

    db.refresh(db_input)
    return db_input


async def run_simulation_generation_task(input_id: str, simulation_id: str, pitch: str):
    from database import SessionLocal 
    db = SessionLocal()
    
    try:
        new_simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        scenario_data = await generate(pitch)
        
        new_simulation.scene_organization = scenario_data.scene_organization
        new_simulation.case_presentation = scenario_data.case_presentation
        new_simulation.students_briefing = scenario_data.students_briefing
        new_simulation.debriefing = scenario_data.debriefing
        new_simulation.appendix = scenario_data.appendix
        new_simulation.uses_simulator = 1 if scenario_data.scene_participants.uses_simulator else 0
        new_simulation.students_quantity = scenario_data.scene_participants.students_quantity
        new_simulation.actors_quantity = scenario_data.scene_participants.actors_quantity
        new_simulation.students_role = scenario_data.scene_participants.students_role
        new_simulation.actors_role = scenario_data.scene_participants.actors_role
        new_simulation.simulator_role = scenario_data.scene_participants.simulator_role
        new_simulation.simulator_parameters = scenario_data.simulator_parameters
        new_simulation.simulator_evolution_parameters = scenario_data.simulator_evolution_parameters
        
        new_simulation.status = SimulationStatus.COMPLETE

        for actor_brief in scenario_data.actor_briefing:
            db.add(Actor(**actor_brief.model_dump(), simulation_id=simulation_id))

        for index, scene_data in enumerate(scenario_data.scene_flow):
            db.add(Scene(**scene_data.model_dump(), sequence_number=index + 1, simulation_id=simulation_id))

        db.commit()
    except Exception:
        db.rollback()
        sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        sim.status = SimulationStatus.INTERRUPTED
        sim.error = traceback.format_exc()
        db.commit()
    finally:
        db.close()

async def simulation_gen(usr_input: str) -> Scenario:
    """
    Generates a simulation based on input string

    Args:
        usr_input (str): Broad description of the story.

    Returns:
        Scenario: Structured llm output.
    """
    return asyncio.run(main=generate(usr_input=usr_input))


def get_simulations_by_input_id_service(db: Session, simulation_input_id: str):
    """
    Retrieves all simulations associated with a specific input ID.
    SQLAlchemy's lazy loading will handle fetching actors/materials/scenes
    when the Pydantic schema accesses those attributes.
    """
    return db.query(Simulation).filter(Simulation.simulation_input_id == simulation_input_id).all()
