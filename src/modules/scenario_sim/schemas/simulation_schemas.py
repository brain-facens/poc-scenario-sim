from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator
from modules.scenario_sim.schemas.evaluation_schema import EvaluationResponse


class SimulationInputCreate(BaseModel):
    pitch: str
    local_aula: str
    nome_cenario: str
    cursos: str
    componente_curricular: str
    objectives: list[str]
    student_ammount: int
    actors_ammount: int
    uses_simulator: bool
    simulator_description: Optional[str] = None


class SimulationInputRead(BaseModel):
    id: str
    pitch: str
    local_aula: str
    nome_cenario: str
    cursos: str
    componente_curricular: str
    objectives: list[str]
    student_ammount: int
    actors_ammount: int
    uses_simulator: bool
    simulator_description: str | None
    created_at: datetime
    updated_at: datetime | None = None

    @field_validator('objectives', mode='before')
    @classmethod
    def transform_objectives(cls, v):
        if isinstance(v, list) and v and not isinstance(v[0], str):
            return [obj.description for obj in v]
        return v

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
    student_plan_a: str | None
    actor_sim_directions: str | None
    actor_plan_b: str | None
    sequence_number: int | None

    class Config:
        from_attributes: bool = True


class SimulationFullRead(BaseModel):
    id: str
    simulation_input_id: str
    simulation_input: Optional[SimulationInputRead] = None
    learning_objectives: str | None
    status: str
    pdf_status: str
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
    evaluations: list[EvaluationResponse] = []

    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes: bool = True


class SimulationUpdateSchema(BaseModel):
    learning_objectives: Optional[str] = None
    case_presentation: Optional[str] = None
    scene_organization: Optional[str] = None
    students_briefing: Optional[str] = None
    students_role: Optional[str] = None
    actors_role: Optional[str] = None
    simulator_role: Optional[str] = None
    students_quantity: Optional[int] = None
    actors_quantity: Optional[int] = None
    uses_simulator: Optional[int] = None
    debriefing: Optional[str] = None
    appendix: Optional[str] = None
