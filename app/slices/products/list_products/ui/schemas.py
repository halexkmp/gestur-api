from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ProductResponse(BaseModel):
    id: UUID
    name: str
    type: str
    default_price: float
    has_stock: bool
    stock_quantity: int
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
