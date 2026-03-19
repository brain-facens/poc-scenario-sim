from pydantic import BaseModel


class Scene(BaseModel):
    student_plan_a: str
    actor_sim_directions: str
    student_plan_b: str
