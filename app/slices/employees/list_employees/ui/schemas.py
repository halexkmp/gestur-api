from uuid import UUID

from pydantic import BaseModel
from typing import Optional, List

class EmployeeResponse(BaseModel):
    id: UUID
    name: str
    pix_key: Optional[str]
    salary: float
    active: bool

    class Config:
        from_attributes = True

class ListEmployeesResponse(BaseModel):
    items: List[EmployeeResponse]
