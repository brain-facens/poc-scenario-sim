from pydantic import BaseModel
from typing import Optional

class MaterialUpdate(BaseModel):
    material_name: Optional[str] = None
    amount: Optional[int] = None

class MaterialRead(BaseModel):
    id: str
    material_name: str
    amount: int
    simulation_id: str

    class Config:
        from_attributes = True
