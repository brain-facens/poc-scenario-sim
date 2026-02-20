from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SimulationInputCreate(BaseModel):
    pitch: str

class SimulationInputRead(BaseModel):
    id: str
    pitch: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        
class ActorRead(BaseModel):
    id: str
    personal_data: Optional[str]
    current_story: Optional[str]
    previous_story: Optional[str]
    clothing: Optional[str]
    behavior_profile: Optional[str]
    
    class Config:
        from_attributes = True

class MaterialRead(BaseModel):
    id: str
    material_name: str
    amount: int
    
    class Config:
        from_attributes = True

class SceneRead(BaseModel):
    id: str
    student_role: Optional[str]
    actor_sim_role: Optional[str]
    student_plan_b: Optional[str]
    sequence_number: Optional[int]
    
    class Config:
        from_attributes = True

class SimulationFullRead(BaseModel):
    id: str
    simulation_input_id: str
    scene_organization: Optional[str]
    case_presentation: Optional[str]
    students_briefing: Optional[str]
    debriefing: Optional[str]
    appendix: Optional[str]
    
    uses_simulator: int
    students_quantity: Optional[int]
    actors_quantity: Optional[int]
    students_role: Optional[str]
    actors_role: Optional[str]
    simulator_role: Optional[str]
    
    simulator_parameters: Optional[str]
    simulator_evolution_parameters: Optional[str]

    actors: List[ActorRead] = []
    scenes: List[SceneRead] = []
    materials: List[MaterialRead] = []

    class Config:
        from_attributes = True