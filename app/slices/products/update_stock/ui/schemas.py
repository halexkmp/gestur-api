from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.shared.db.enums import StockChangeType


class UpdateStockRequest(BaseModel):
    product_id: UUID
    change_type: StockChangeType
    quantity_change: int
    reason: Optional[str]
    sale_id: Optional[UUID] = None


class StockResponse(BaseModel):
    id: UUID
