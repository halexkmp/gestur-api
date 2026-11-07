from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateDeviceRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class CreateDeviceResponse(BaseModel):
    id: UUID
    name: str
    active: bool
    created_at: datetime
    api_key: str
