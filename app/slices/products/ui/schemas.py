from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class ProductBase(BaseModel):
    name: str
    type: str
    default_price: float
    has_stock: bool = False
    stock_quantity: int = 0
    active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    default_price: Optional[float] = None
    has_stock: Optional[bool] = None
    stock_quantity: Optional[int] = None
    active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
