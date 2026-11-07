from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field


class RecordTripRequest(BaseModel):
    id: UUID
    start: AwareDatetime
    end: AwareDatetime
    passengers: int = Field(ge=1, le=10)


class RecordTripResponse(BaseModel):
    id: UUID
    duplicate: bool
