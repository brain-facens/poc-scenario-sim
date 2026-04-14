from typing import Optional

from pydantic import BaseModel


class SceneCreate(BaseModel):
    simulation_id: str
    student_plan_a: Optional[str] = None
    actor_sim_directions: Optional[str] = None
    actor_plan_b: Optional[str] = None
    sequence_number: Optional[int] = None


class SceneUpdate(BaseModel):
    student_plan_a: Optional[str] = None
    actor_sim_directions: Optional[str] = None
    sequence_number: Optional[int] = None
    actor_plan_b: Optional[str] = None


class SceneRead(BaseModel):
    id: str
    student_plan_a: Optional[str]
    actor_sim_directions: Optional[str]
    actor_plan_b: Optional[str]
    sequence_number: Optional[int]
    simulation_id: str

    class Config:
        from_attributes = True
