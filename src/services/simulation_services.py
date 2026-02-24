import asyncio

from sqlalchemy.orm import Session

from gen_tests.gen_parts.scenario import Scenario
from gen_tests.gen_sim import generate
from models import Actor, Material, Scene, Simulation, SimulationInput
from schemas.simulation_input_schemas import SimulationInputCreate


async def create_simulation_input_service(db: Session, input_data: SimulationInputCreate):
    """
    Creates a new SimulationInput record and populates the simulation 
    tables with generated data from the LLM.
    """
    db_input = SimulationInput(pitch=input_data.pitch)
    db.add(db_input)
    db.commit()
    db.refresh(db_input)

    scenario_data = await generate(input_data.pitch)
    
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
        simulator_evolution_parameters=scenario_data.simulator_evolution_parameters
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
            simulation_id=new_simulation.id
        )
        db.add(db_actor)

    for index, scene_data in enumerate(scenario_data.scene_flow):
        db_scene = Scene(
            student_role=scene_data.student_role,
            actor_sim_role=scene_data.actor_sim_role,
            student_plan_b=scene_data.student_plan_b,
            sequence_number=index + 1,
            simulation_id=new_simulation.id
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
    return asyncio.run(main=generate(usr_input=usr_input))


def get_simulations_by_input_id_service(db: Session, simulation_input_id: str):
    """
    Retrieves all simulations associated with a specific input ID.
    SQLAlchemy's lazy loading will handle fetching actors/materials/scenes
    when the Pydantic schema accesses those attributes.
    """
    return db.query(Simulation).filter(Simulation.simulation_input_id == simulation_input_id).all()
