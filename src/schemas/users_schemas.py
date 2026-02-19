from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from models.users_model import UserRole

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[UserRole] = UserRole.USER
    
class UserRead(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

class UserPaginated(BaseModel):
    total: int
    page: int
    limit: int
    users: list[UserRead]

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None