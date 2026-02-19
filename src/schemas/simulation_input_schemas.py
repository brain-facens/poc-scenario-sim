from pydantic import BaseModel
from typing import Optional
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