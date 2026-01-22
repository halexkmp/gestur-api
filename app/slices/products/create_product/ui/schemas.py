from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    type: str
    default_price: float
    has_stock: bool = False
    stock_quantity: int = 0
    active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
