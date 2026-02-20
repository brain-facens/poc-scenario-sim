from pydantic import BaseModel


class Scene(BaseModel):
    student_role: str
    actor_sim_role: str
    student_plan_b: str
