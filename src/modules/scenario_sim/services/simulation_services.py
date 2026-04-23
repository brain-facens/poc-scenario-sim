import asyncio
import traceback
from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from modules.scenario_sim.gen_engine.export_sim import export_docx
from modules.scenario_sim.gen_engine.gen_parts.scenario import Scenario
from modules.scenario_sim.gen_engine.gen_sim import generate
from modules.scenario_sim.models import (
    Actor,
    Material,
    Scene,
    Simulation,
    SimulationInput,
    SimulationInputObjective,
)
from modules.scenario_sim.models.simulation_model import PdfStatus, SimulationStatus
from modules.scenario_sim.schemas.simulation_schemas import (
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
    if not input_data.objectives or not (1 <= len(input_data.objectives) <= 3):
        raise HTTPException(
            status_code=400,
            detail="Learning objectives must have between 1 and 3 items.",
        )

    db_input = SimulationInput(
        pitch=input_data.pitch,
        local_aula=input_data.local_aula,
        nome_cenario=input_data.nome_cenario,
        cursos=input_data.cursos,
        componente_curricular=input_data.componente_curricular,
        student_ammount=input_data.student_ammount,
        actors_ammount=input_data.actors_ammount,
        uses_simulator=input_data.uses_simulator,
        simulator_description=input_data.simulator_description,
    )
    db.add(db_input)
    db.flush()  # To get db_input.id

    for obj_desc in input_data.objectives:
        db_obj = SimulationInputObjective(
            description=obj_desc, simulation_input_id=db_input.id
        )
        db.add(db_obj)

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
            input_data.objectives,
            input_data.student_ammount,
            input_data.actors_ammount,
            input_data.uses_simulator,
            input_data.simulator_description,
        )

    db.refresh(db_input)

    return db_input


async def run_simulation_generation_task(
    input_id: str,
    simulation_id: str,
    pitch: str,
    objectives: list[str] | list[SimulationInputObjective],
    student_ammount: int,
    actors_ammount: int,
    uses_simulator: bool,
    simulator_description: str | None,
):

    if objectives and not isinstance(objectives[0], str):
        objectives = [obj.description for obj in objectives]

    from database import SessionLocal

    db = SessionLocal()

    try:
        new_simulation = (
            db.query(Simulation).filter(Simulation.id == simulation_id).first()
        )

        scenario_data = await generate(pitch)

        new_simulation.scene_organization = scenario_data.scene_organization
        new_simulation.learning_objectives = scenario_data.learning_objectives
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

        print(f"Scenario generated for {simulation_id}, generating PDF...")
        new_simulation.pdf_status = PdfStatus.GENERATING
        db.commit()

        pdf_result_path = await export_docx(scenario_data)
        new_simulation.pdf_path = pdf_result_path
        new_simulation.pdf_status = PdfStatus.READY
        new_simulation.updated_at = func.now()

        db.commit()
        db.refresh(new_simulation)
        print(f"✅ Initial PDF generated and saved to: {pdf_result_path}")
    except Exception:
        db.rollback()
        sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        sim.status = SimulationStatus.INTERRUPTED
        sim.pdf_status = PdfStatus.ERROR
        sim.error = traceback.format_exc()
        db.commit()
    finally:
        db.close()


async def simulation_gen(usr_input: str) -> Scenario:
    """
    Generates a simulation based on input string.

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
    scenario.pdf_path = await generate_and_save_pdf_service(scenario)
    print("Done!")
    return scenario


def get_simulation_by_id_service(db: Session, simulation_id: str):
    """Retrieves a single simulation by its ID."""
    return db.query(Simulation).filter(Simulation.id == simulation_id).first()


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


from typing import Optional

from core.pagination import paginate_and_filter
from modules.scenario_sim.models import SimulationInput


def get_all_simulation_ids_service(
    db: Session,
    page: int = 1,
    limit: int = 10,
    status: Optional[str] = None,
    learning_objectives: Optional[str] = None,
    pitch: Optional[str] = None,
):
    """Retrieves simulations using pagination and filters."""
    query = db.query(Simulation)

    if pitch:
        query = query.join(SimulationInput).filter(
            SimulationInput.pitch.ilike(f"%{pitch}%")
        )

    filters = {"status": status, "learning_objectives": learning_objectives}
    return paginate_and_filter(
        db=db, model=Simulation, page=page, limit=limit, filters=filters, query=query
    )


def cleanup_timed_out_simulations(db: Session, timeout_minutes: int = 5):
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
                next_sim.simulation_input.objectives,
                next_sim.simulation_input.student_ammount,
                next_sim.simulation_input.actors_ammount,
                next_sim.simulation_input.uses_simulator,
                next_sim.simulation_input.simulator_description,
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


async def generate_and_save_pdf_service(
    db: Session, simulation_id: str, background_tasks: BackgroundTasks
) -> bool:
    """Service to trigger a new PDF generation in the background."""
    simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()

    if not simulation:
        return False

    simulation.pdf_status = PdfStatus.GENERATING
    db.commit()

    background_tasks.add_task(run_pdf_generation_task, simulation_id)

    return True


async def run_pdf_generation_task(simulation_id: str):
    import traceback

    from database import SessionLocal

    db = SessionLocal()

    try:
        simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if not simulation:
            print(
                f"❌ Error: Simulation {simulation_id} not found for PDF generation task."
            )
            return

        print(f"Regenerating PDF for Simulation {simulation_id}...")
        pdf_path = await export_docx(simulation.to_scenario())

        simulation.pdf_path = pdf_path
        simulation.pdf_status = PdfStatus.READY
        simulation.updated_at = func.now()

        db.commit()
        db.refresh(simulation)
        print(f"✅ PDF regenerated and saved to: {pdf_path}")
    except Exception:
        db.rollback()
        simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if simulation:
            simulation.pdf_status = PdfStatus.ERROR
            db.commit()
        print(traceback.format_exc())
    finally:
        db.close()
