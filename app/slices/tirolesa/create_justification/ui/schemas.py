from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.db.enums import TirolesaJustificationType


class CreateJustificationRequest(BaseModel):
    audit_date: date
    quantity: int = Field(ge=1)
    type: TirolesaJustificationType
    reason: str = Field(min_length=1)


class CreateJustificationResponse(BaseModel):
    id: UUID
    audit_date: date
    quantity: int
    type: TirolesaJustificationType
    reason: str
    created_at: datetime
