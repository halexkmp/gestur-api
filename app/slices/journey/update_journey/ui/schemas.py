from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UpdateJourneyRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: Optional[datetime] = None
    edit_reason: str
