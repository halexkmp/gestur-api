from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.shared.db.enums import StockChangeType


class UpdateStockRequest(BaseModel):
    product_id: UUID
    change_type: StockChangeType
    quantity_change: int
    sale_id: Optional[UUID] = None


class StockResponse(BaseModel):
    id: UUID
    change_type: StockChangeType
    created_at: datetime
    product_id: UUID
    quantity_change: int
    sale_id: Optional[UUID] = None
    user_id: UUID
