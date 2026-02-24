from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import List
from app.shared.db.enums import UserRole

class UserCreate(BaseModel):
    name: str
    username: str
    password: str
    roles: List[UserRole] = [UserRole.OPERATOR]

class UserResponse(BaseModel):
    id: UUID
    name: str
    username: str
    roles: List[UserRole]
    created_at: datetime

    class Config:
        from_attributes = True
