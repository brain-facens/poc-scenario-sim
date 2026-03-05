from datetime import datetime

from pydantic import BaseModel


class SimulationInputCreate(BaseModel):
    pitch: str


class SimulationInputRead(BaseModel):
    id: str
    pitch: str
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes: bool = True


class ActorRead(BaseModel):
    id: str
    personal_data: str | None
    current_story: str | None
    previous_story: str | None
    clothing: str | None
    behavior_profile: str | None

    class Config:
        from_attributes: bool = True


class MaterialRead(BaseModel):
    id: str
    material_name: str
    amount: int

    class Config:
        from_attributes: bool = True


class SceneRead(BaseModel):
    id: str
    student_role: str | None
    actor_sim_role: str | None
    student_plan_b: str | None
    sequence_number: int | None

    class Config:
        from_attributes: bool = True


class SimulationFullRead(BaseModel):
    id: str
    simulation_input_id: str
    status: str
    error: str | None = None
    scene_organization: str | None
    case_presentation: str | None
    students_briefing: str | None
    debriefing: str | None
    appendix: str | None

    uses_simulator: int
    students_quantity: int | None
    actors_quantity: int | None
    students_role: str | None
    actors_role: str | None
    simulator_role: str | None

    simulator_parameters: str | None
    simulator_evolution_parameters: str | None

    actors: list[ActorRead] = []
    scenes: list[SceneRead] = []
    materials: list[MaterialRead] = []
    
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes: bool = True
