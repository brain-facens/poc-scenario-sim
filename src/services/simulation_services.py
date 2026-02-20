import asyncio

from sqlalchemy.orm import Session

from gen_tests.gen_parts.scenario import Scenario
from gen_tests.gen_sim import generate
from models import Actor, Material, Scene, Simulation, SimulationInput
from schemas.simulation_input_schemas import SimulationInputCreate


async def create_simulation_input_service(db: Session, input_data: SimulationInputCreate):
    """
    Creates a new SimulationInput record in the database.
    """
    db_input = SimulationInput(pitch=input_data.pitch)

    db.add(db_input)
    db.commit()
    db.refresh(db_input)

    #create_mock_simulation_service(db, db_input.id)
    test = await generate(input_data.pitch)
    print("TESTE", test)
    
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
    Creates a full simulation based on the specific JSON structure provided.
    """
    new_simulation = Simulation(
        simulation_input_id=simulation_input_id,
        scene_organization="A simulação é dividida em três cenas principais...", # New field
        case_presentation="Idoso apresenta sintomas inespecíficos (fadiga, dores musculares...)",
        students_briefing="Você é o médico responsável pelo atendimento domiciliar...", # Plural
        debriefing="Ao final, discutir como foi abordado o medo do paciente...",
        appendix="- Materiais sugeridos: poltrona, manta, jaleco...",
        
        uses_simulator=False,
        students_quantity=1,
        actors_quantity=1,
        students_role="Médico responsável pelo atendimento domiciliar.",
        actors_role="Idoso (paciente) com medo de agulhas.",
        simulator_parameters="",
        simulator_evolution_parameters=""
    )

    mock_actors = [
        Actor(
            personal_data="Nome: Joaquim dos Santos, 78 anos.",
            current_story="Vem apresentando há 5 dias cansaço, inapetência...", # Corrected key
            previous_story="Já se recusou em UBS e hospital a realizar exames...", # Corrected key
            clothing="Pijama, chinelos, sentado em poltrona.",
            behavior_profile="Inicia a consulta colaborativo, mas fica ansioso."
        )
    ]
    new_simulation.actors.extend(mock_actors)

    mock_scenes = [
        Scene(
            student_role="Médico inicia consulta domiciliar, realiza anamnese...",
            actor_sim_role="Paciente inicia colaborativo, mas demonstra inquietação.",
            student_plan_b="Caso perceba ansiedade, pode suspender sugestão de coleta."
        ),
        Scene(
            student_role="Explora e valida sentimentos do paciente...",
            actor_sim_role="Paciente relata experiências passadas traumáticas.",
            student_plan_b="Sugerir métodos alternativos se o paciente insistir no medo."
        )
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
