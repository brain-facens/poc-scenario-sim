from pydantic import BaseModel
from typing import Optional

class ActorUpdate(BaseModel):
    personal_data: Optional[str] = None
    current_story: Optional[str] = None
    previous_story: Optional[str] = None
    clothing: Optional[str] = None
    behavior_profile: Optional[str] = None

class ActorRead(BaseModel):
    id: str
    personal_data: Optional[str]
    current_story: Optional[str]
    previous_story: Optional[str]
    clothing: Optional[str]
    behavior_profile: Optional[str]
    simulation_id: str

    class Config:
        from_attributes = True
