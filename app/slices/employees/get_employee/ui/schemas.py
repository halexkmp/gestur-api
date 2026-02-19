from uuid import UUID

from pydantic import BaseModel
from typing import Optional

class EmployeeResponse(BaseModel):
    id: UUID
    name: str
    pix_key: Optional[str]
    salary: float
    active: bool

    class Config:
        from_attributes = True
