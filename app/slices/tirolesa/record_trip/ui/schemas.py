from uuid import UUID

from pydantic import AwareDatetime, BaseModel


class RecordTripRequest(BaseModel):
    id: UUID
    start: AwareDatetime
    end: AwareDatetime


class RecordTripResponse(BaseModel):
    id: UUID
    duplicate: bool
