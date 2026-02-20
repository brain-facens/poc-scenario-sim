from pydantic import BaseModel


class Participants(BaseModel):
    uses_simulator: bool
    students_quantity: int
    actors_quantity: int
    students_role: str
    actors_role: str
    simulator_role: str
