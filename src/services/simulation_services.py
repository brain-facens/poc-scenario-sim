import asyncio
import traceback
from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks
from sqlalchemy import func
from sqlalchemy.orm import Session

from gen_tests.export_sim import export_pdf
from gen_tests.gen_parts.scenario import Scenario
from gen_tests.gen_sim import generate
from models import Actor, Scene, Simulation, SimulationInput
from models.material_model import Material
from models.simulation_model import SimulationStatus
from schemas.simulation_input_schemas import (
    SimulationInputCreate,
    SimulationUpdateSchema,
)


async def create_simulation_input_service(
    db: Session, input_data: SimulationInputCreate, background_tasks: BackgroundTasks
):
    """
    Creates a new SimulationInput record and populates the simulation
    tables with generated data from the LLM.
    """
    db_input = SimulationInput(pitch=input_data.pitch)
    db.add(db_input)
    db.commit()
    db.refresh(db_input)

    active_exists = (
        db.query(Simulation).filter(Simulation.status == SimulationStatus.DOING).first()
        is not None
    )

    initial_status = SimulationStatus.STALE if active_exists else SimulationStatus.DOING

    new_simulation = Simulation(simulation_input_id=db_input.id, status=initial_status)
    db.add(new_simulation)
    db.commit()

    if initial_status == SimulationStatus.DOING:
        background_tasks.add_task(
            run_simulation_generation_task,
            db_input.id,
            new_simulation.id,
            input_data.pitch,
        )

    db.refresh(db_input)

    return db_input


async def run_simulation_generation_task(input_id: str, simulation_id: str, pitch: str):
    from database import SessionLocal

    db = SessionLocal()

    try:
        new_simulation = (
            db.query(Simulation).filter(Simulation.id == simulation_id).first()
        )
        scenario_data = await generate(pitch)

        new_simulation.scene_organization = scenario_data.scene_organization
        new_simulation.case_presentation = scenario_data.case_presentation
        new_simulation.students_briefing = scenario_data.students_briefing
        new_simulation.debriefing = scenario_data.debriefing
        new_simulation.appendix = scenario_data.appendix
        new_simulation.uses_simulator = (
            1 if scenario_data.scene_participants.uses_simulator else 0
        )
        new_simulation.students_quantity = (
            scenario_data.scene_participants.students_quantity
        )
        new_simulation.actors_quantity = (
            scenario_data.scene_participants.actors_quantity
        )
        new_simulation.students_role = scenario_data.scene_participants.students_role
        new_simulation.actors_role = scenario_data.scene_participants.actors_role
        new_simulation.simulator_role = scenario_data.scene_participants.simulator_role
        new_simulation.simulator_parameters = scenario_data.simulator_parameters
        new_simulation.simulator_evolution_parameters = (
            scenario_data.simulator_evolution_parameters
        )

        new_simulation.status = SimulationStatus.COMPLETE

        for actor_brief in scenario_data.actor_briefing:
            db.add(Actor(**actor_brief.model_dump(), simulation_id=simulation_id))

        for resource in scenario_data.necessary_resources:
            db_material = Material(
                material_name=resource.name,
                amount=resource.quantity,
                simulation_id=simulation_id,
            )
            db.add(db_material)

        for index, scene_data in enumerate(scenario_data.scene_flow):
            db_scene = Scene(
                **scene_data.model_dump(),
                sequence_number=index + 1,
                simulation_id=simulation_id,
            )
            db.add(db_scene)

        print("Scenario generated, generating PDF...")
        new_simulation.pdf_path = await export_pdf(scenario_data)

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
    print("Generating scenario...")
    scenario: Scenario = await generate(usr_input=usr_input)
    import os

    os.makedirs("./scenarios", exist_ok=True)
    with open("./scenarios/test.json", "w", encoding="utf-8") as file:
        file.write(scenario.model_dump_json(indent=4))
    print("Scenario generated, generating PDF...")
    scenario.pdf_path = await generate_pdf(scenario)
    print("Done!")
    return scenario


async def generate_pdf(sim_data: Scenario) -> str:
    return await export_pdf(sim_data)


def get_simulations_by_input_id_service(db: Session, simulation_input_id: str):
    """
    Retrieves all simulations associated with a specific input ID.
    SQLAlchemy's lazy loading will handle fetching actors/materials/scenes
    when the Pydantic schema accesses those attributes.
    """
    return (
        db.query(Simulation)
        .filter(Simulation.simulation_input_id == simulation_input_id)
        .all()
    )


def get_all_simulation_ids_service(db: Session):
    """
    Retrieves all simulation IDs from the database.
    """
    return db.query(Simulation).distinct().all()


def cleanup_timed_out_simulations(db: Session, timeout_minutes: int = 3):
    now = datetime.now(timezone.utc)
    threshold = now - timedelta(minutes=timeout_minutes)
    print(
        f"Watchdog: Checking for simulations stuck since before {threshold.isoformat()}"
    )

    timed_out_sims = (
        db.query(Simulation)
        .filter(
            Simulation.status == SimulationStatus.DOING,
            func.coalesce(Simulation.updated_at, Simulation.created_at) < threshold,
        )
        .all()
    )

    print(f"Watchdog: Found {len(timed_out_sims)} timed-out simulations.")

    for sim in timed_out_sims:
        sim.status = SimulationStatus.INTERRUPTED
        sim.error = "hard timeout error"

    db.commit()
    return len(timed_out_sims)


async def process_stale_queue(db: Session):
    """Promotes the most recent STALE simulation to DOING if none are active."""
    active_job = (
        db.query(Simulation).filter(Simulation.status == SimulationStatus.DOING).first()
    )

    if active_job:
        return None

    next_sim = (
        db.query(Simulation)
        .filter(Simulation.status == SimulationStatus.STALE)
        .order_by(Simulation.created_at.desc())
        .first()
    )

    print(f"Watchdog: Found next stale simulation: {next_sim.id if next_sim else None}")

    if next_sim:
        next_sim.status = SimulationStatus.DOING
        db.commit()

        asyncio.create_task(
            run_simulation_generation_task(
                next_sim.simulation_input_id,
                next_sim.id,
                next_sim.simulation_input.pitch,
            )
        )
        return next_sim.id

    return None


def update_simulation_service(
    db: Session, simulation_id: str, update_data: SimulationUpdateSchema
):
    simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()

    if not simulation:
        return None

    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(simulation, key, value)

    db.commit()
    db.refresh(simulation)
    return simulation
