import asyncio

from sqlalchemy.orm import Session

from gen_tests.gen_parts.scenario import Scenario
from gen_tests.gen_sim import generate
from models import Actor, Material, Scene, Simulation, SimulationInput
from schemas.simulation_input_schemas import SimulationInputCreate


def create_simulation_input_service(db: Session, input_data: SimulationInputCreate):
    """
    Creates a new SimulationInput record in the database.
    """
    db_input = SimulationInput(pitch=input_data.pitch)

    db.add(db_input)
    db.commit()
    db.refresh(db_input)

    create_mock_simulation_service(db, db_input.id)

    return db_input


async def simulation_gen(usr_input: str) -> Scenario:
    """
    Generates a simulation based on input string

    Args:
        usr_input (str): Broad description of the story.

    Returns:
        Scenario: Structured llm output.
    """
    return asyncio.run(main=generate(usr_input=usr_input))


def create_mock_simulation_service(db: Session, simulation_input_id: str):
    """
    Creates a full mock simulation with related actors, materials, and scenes
    linked to a specific SimulationInput.
    """

    new_simulation = Simulation(
        simulation_input_id=simulation_input_id,
        scenario_name="Emergency Room Protocol",
        class_location="Lab 402",
        teacher_name="Dr. Smith",
        time_duration=60,
        class_objectives="Identify early signs of cardiac arrest.",
        ambience_description="High-pressure hospital environment with beeping monitors.",
        case_presentation="A 55-year-old male arrives complaining of chest pain.",
        student_briefing="Prepare the patient for an ECG.",
        debriefing="Review communication clarity and speed of intervention.",
    )

    mock_actors = [
        Actor(
            personal_data="John Doe, 55 years old",
            current_history="Chest pain for 2 hours",
            clothing="Hospital gown",
            behavior_profile="Anxious and sweating",
        ),
        Actor(
            personal_data="Nurse Jane",
            current_history="Assisting the primary doctor",
            clothing="Blue scrubs",
            behavior_profile="Professional and helpful",
        ),
    ]
    new_simulation.actors.extend(mock_actors)

    mock_materials = [
        Material(material_name="ECG Machine", amount=1),
        Material(material_name="Latex Gloves", amount=50),
        Material(material_name="Stethoscope", amount=1),
    ]
    new_simulation.materials.extend(mock_materials)

    mock_scenes = [
        Scene(name="Arrival", description="The patient enters via ambulance."),
        Scene(name="Examination", description="Students perform the initial assessment."),
        Scene(name="Conclusion", description="The patient is stabilized."),
    ]
    new_simulation.scenes.extend(mock_scenes)

    db.add(new_simulation)
    db.commit()
    db.refresh(new_simulation)

    return new_simulation


def get_simulations_by_input_id_service(db: Session, simulation_input_id: str):
    """
    Retrieves all simulations associated with a specific input ID.
    SQLAlchemy's lazy loading will handle fetching actors/materials/scenes
    when the Pydantic schema accesses those attributes.
    """
    return db.query(Simulation).filter(Simulation.simulation_input_id == simulation_input_id).all()
