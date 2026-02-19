from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SimulationInputCreate(BaseModel):
    """Schema for creating a new SimulationInput."""
    pitch: str

class SimulationInputRead(BaseModel):
    """Schema for reading a SimulationInput from the database."""
    id: str
    pitch: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        
class ActorRead(BaseModel):
    id: str
    personal_data: Optional[str]
    current_history: Optional[str]
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
    name: str
    description: Optional[str]
    class Config:
        from_attributes = True

# --- Parent Simulation Schema ---
class SimulationFullRead(BaseModel):
    id: str
    scenario_name: Optional[str]
    class_location: Optional[str]
    teacher_name: Optional[str]
    time_duration: Optional[int]
    class_objectives: Optional[str]
    ambience_description: Optional[str]
    case_presentation: Optional[str]
    student_briefing: Optional[str]
    debriefing: Optional[str]
    
    # These field names must match the 'relationship' names in simulation_model.py
    actors: List[ActorRead] = []
    materials: List[MaterialRead] = []
    scenes: List[SceneRead] = []

    class Config:
        from_attributes = True