from datetime import date as DateType, datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.shared.db.enums import TirolesaAuditStatus, TirolesaJustificationType


class JustificationUser(BaseModel):
    id: UUID
    name: str


class AuditJustification(BaseModel):
    id: UUID
    quantity: int
    type: TirolesaJustificationType
    reason: str
    created_by: JustificationUser
    created_at: datetime


class AuditDayResponse(BaseModel):
    date: DateType
    passengers_detected: int
    passengers_sold: int
    passengers_below_default_price: int
    passengers_justified: int
    unexplained: int
    sold_above_detected: int
    sales_amount: float
    estimated_unpaid_value: float
    status: TirolesaAuditStatus
    device_hours: int
    clock_suspect_trips: int
    sensor_warning: bool
    justifications: List[AuditJustification]
