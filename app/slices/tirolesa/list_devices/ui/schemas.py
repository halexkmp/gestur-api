from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DeviceResponse(BaseModel):
    id: UUID
    name: str
    active: bool
    last_seen_at: Optional[datetime]
    offline: bool
