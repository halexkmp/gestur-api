from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class RegisterJourneyRequest(BaseModel):
    latitude: float
    longitude: float

class JourneyResponse(BaseModel):
    id: UUID
    user_id: UUID
    timestamp: datetime
    latitude: float
    longitude: float

    class Config:
        from_attributes = True
