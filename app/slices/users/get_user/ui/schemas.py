from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.shared.db.enums import UserRole

class UserResponse(BaseModel):
    id: UUID
    name: str
    username: str
    role: UserRole
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True
