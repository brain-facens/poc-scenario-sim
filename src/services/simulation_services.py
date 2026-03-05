import asyncio

from sqlalchemy.orm import Session

from gen_tests.export_sim import export_pdf
from gen_tests.gen_parts.scenario import Scenario
from gen_tests.gen_sim import generate
from models import Actor, Scene, Simulation, SimulationInput
from models.material_model import Material
from schemas.simulation_input_schemas import SimulationInputCreate


async def create_simulation_input_service(
    db: Session, input_data: SimulationInputCreate
):
    """
    Creates a new SimulationInput record and populates the simulation
    tables with generated data from the LLM.
    """
    db_input = SimulationInput(pitch=input_data.pitch)
    db.add(db_input)
    db.commit()
    db.refresh(db_input)

    scenario_data = await simulation_gen(input_data.pitch)

    new_simulation = Simulation(
        simulation_input_id=db_input.id,
        scene_organization=scenario_data.scene_organization,
        case_presentation=scenario_data.case_presentation,
        students_briefing=scenario_data.students_briefing,
        debriefing=scenario_data.debriefing,
        appendix=scenario_data.appendix,
        uses_simulator=1 if scenario_data.scene_participants.uses_simulator else 0,
        students_quantity=scenario_data.scene_participants.students_quantity,
        actors_quantity=scenario_data.scene_participants.actors_quantity,
        students_role=scenario_data.scene_participants.students_role,
        actors_role=scenario_data.scene_participants.actors_role,
        simulator_role=scenario_data.scene_participants.simulator_role,
        simulator_parameters=scenario_data.simulator_parameters,
        simulator_evolution_parameters=scenario_data.simulator_evolution_parameters,
    )
    db.add(new_simulation)
    db.flush()

    for actor_brief in scenario_data.actor_briefing:
        db_actor = Actor(
            personal_data=actor_brief.personal_data,
            current_story=actor_brief.current_story,
            previous_story=actor_brief.previous_story,
            clothing=actor_brief.clothing,
            behavior_profile=actor_brief.behavior_profile,
            simulation_id=new_simulation.id,
        )
        db.add(db_actor)

    for resource in scenario_data.necessary_resources:
        db_material = Material(
            material_name=resource.name,
            amount=resource.quantity,
            simulation_id=new_simulation.id,
        )
        db.add(db_material)

    for index, scene_data in enumerate(scenario_data.scene_flow):
        db_scene = Scene(
            student_role=scene_data.student_role,
            actor_sim_role=scene_data.actor_sim_role,
            student_plan_b=scene_data.student_plan_b,
            sequence_number=index + 1,
            simulation_id=new_simulation.id,
        )
        db.add(db_scene)

    db.commit()
    db.refresh(db_input)

    return db_input


async def simulation_gen(usr_input: str) -> Scenario:
    """
    Generates a simulation based on input string

    Args:
        usr_input (str): Broad description of the story.

    Returns:
        Scenario: Structured llm output.
    """
    scenario: Scenario = asyncio.run(main=generate(usr_input=usr_input))
    with open("./scenarios/test.json", "w", encoding="utf-8") as file:
        file.write(scenario.model_dump_json(indent=4))
    return scenario


async def generate_pdf(sim_data: Simulation) -> str:
    scenario: Scenario = sim_data.to_scenario()
    return await export_pdf(scenario)


def create_mock_simulation_service(db: Session, simulation_input_id: str):
    """
    Creates a full simulation based on the specific JSON structure provided.
    """
    new_simulation = Simulation(
        simulation_input_id=simulation_input_id,
        scene_organization="A simulação é dividida em três cenas principais...",  # New field
        case_presentation="Idoso apresenta sintomas inespecíficos (fadiga, dores musculares...)",
        students_briefing="Você é o médico responsável pelo atendimento domiciliar...",  # Plural
        debriefing="Ao final, discutir como foi abordado o medo do paciente...",
        appendix="- Materiais sugeridos: poltrona, manta, jaleco...",
        uses_simulator=False,
        students_quantity=1,
        actors_quantity=1,
        students_role="Médico responsável pelo atendimento domiciliar.",
        actors_role="Idoso (paciente) com medo de agulhas.",
        simulator_parameters="",
        simulator_evolution_parameters="",
    )

    mock_actors = [
        Actor(
            personal_data="Nome: Joaquim dos Santos, 78 anos.",
            current_story="Vem apresentando há 5 dias cansaço, inapetência...",  # Corrected key
            previous_story="Já se recusou em UBS e hospital a realizar exames...",  # Corrected key
            clothing="Pijama, chinelos, sentado em poltrona.",
            behavior_profile="Inicia a consulta colaborativo, mas fica ansioso.",
        )
    ]
    new_simulation.actors.extend(mock_actors)

    mock_scenes = [
        Scene(
            student_role="Médico inicia consulta domiciliar, realiza anamnese...",
            actor_sim_role="Paciente inicia colaborativo, mas demonstra inquietação.",
            student_plan_b="Caso perceba ansiedade, pode suspender sugestão de coleta.",
        ),
        Scene(
            student_role="Explora e valida sentimentos do paciente...",
            actor_sim_role="Paciente relata experiências passadas traumáticas.",
            student_plan_b="Sugerir métodos alternativos se o paciente insistir no medo.",
        ),
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
