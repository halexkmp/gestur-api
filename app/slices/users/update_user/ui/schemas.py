from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.shared.db.enums import UserRole

class UserUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None

class UserResponse(BaseModel):
    id: UUID
    name: str
    username: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True
