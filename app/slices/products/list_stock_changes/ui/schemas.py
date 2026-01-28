from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.shared.db.enums import StockChangeType

class ProductResponse(BaseModel):
    id: UUID
    name: str
    stock_quantity: int
    class Config:
        from_attributes = True

class SaleResponse(BaseModel):
    id: UUID
    sale_code: str
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: UUID
    name: str
    class Config:
        from_attributes = True

class StockResponse(BaseModel):
    id: UUID
    change_type: StockChangeType
    created_at: datetime
    product: ProductResponse
    quantity_change: int
    sale: Optional[SaleResponse] = None
    user: UserResponse
    class Config:
        from_attributes = True
