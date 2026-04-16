from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class EvaluationBase(BaseModel):
    simulation_id: str
    explanation: str
    grade: float

class EvaluationCreate(EvaluationBase):
    pass

class EvaluationUpdate(BaseModel):
    explanation: Optional[str] = None
    grade: Optional[float] = None

class EvaluationResponse(EvaluationBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
