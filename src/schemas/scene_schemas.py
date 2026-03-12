from pydantic import BaseModel
from typing import Optional

class SceneCreate(BaseModel):
    simulation_id: str
    student_role: Optional[str] = None
    actor_sim_role: Optional[str] = None
    student_plan_b: Optional[str] = None
    sequence_number: Optional[int] = None

class SceneUpdate(BaseModel):
    student_role: Optional[str] = None
    actor_sim_role: Optional[str] = None
    student_plan_b: Optional[str] = None

class SceneRead(BaseModel):
    id: str
    student_role: Optional[str]
    actor_sim_role: Optional[str]
    student_plan_b: Optional[str]
    sequence_number: Optional[int]
    simulation_id: str

    class Config:
        from_attributes = True
