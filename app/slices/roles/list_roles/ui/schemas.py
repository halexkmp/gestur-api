from pydantic import BaseModel
from uuid import UUID


class RoleResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True
