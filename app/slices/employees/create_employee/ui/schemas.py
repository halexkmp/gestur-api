from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field
from typing import Optional

class CreateEmployeeRequest(BaseModel):
    name: str = Field(..., max_length=255)
    pix_key: Optional[str] = Field(default=None, max_length=255)
    salary: float = Field(..., ge=0)
    active: bool = True
    start_date: date
    user_id: Optional[UUID] = None

class EmployeeResponse(BaseModel):
    id: UUID
    name: str
    pix_key: Optional[str]
    salary: float
    active: bool
    start_date: date
    user_id: Optional[UUID]

    class Config:
        from_attributes = True
