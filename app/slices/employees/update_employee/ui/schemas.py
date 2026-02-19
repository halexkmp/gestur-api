from uuid import UUID

from pydantic import BaseModel, Field
from typing import Optional

class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    pix_key: Optional[str] = Field(default=None, max_length=255)
    salary: Optional[float] = Field(default=None, ge=0)
    active: Optional[bool] = None

class EmployeeResponse(BaseModel):
    id: UUID
    name: str
    pix_key: Optional[str]
    salary: float
    active: bool

    class Config:
        from_attributes = True
