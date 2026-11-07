from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UpdateDeviceRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    active: Optional[bool] = None


class UpdateDeviceResponse(BaseModel):
    id: UUID
    name: str
    active: bool
    last_seen_at: Optional[datetime]
