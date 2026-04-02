from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RequestLogRead(BaseModel):
    id: str
    method: str
    path: str
    query_params: Optional[str] = None
    client_ip: Optional[str] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    status_code: int
    response_message: Optional[str] = None
    duration_ms: float
    error_type: Optional[str] = None
    error_detail: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
