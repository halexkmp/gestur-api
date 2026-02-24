from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.shared.db.enums import UserRole


class RoleUpdate(BaseModel):
    id: UUID

class RoleResponse(BaseModel):
    id: UUID
    name: UserRole

class UserUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    roles: Optional[List[RoleUpdate]] = None
    active: Optional[bool] = None

class UserResponse(BaseModel):
    id: UUID
    name: str
    username: str
    roles: List[RoleResponse]
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True
