from typing import List

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.shared.db.enums import UserRole

class RoleResponse(BaseModel):
    id: UUID
    name: UserRole

class UserResponse(BaseModel):
    id: UUID
    name: str
    username: str
    roles: List[RoleResponse]
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True
