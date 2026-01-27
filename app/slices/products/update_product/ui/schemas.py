from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class ProductBase(BaseModel):
    name: str
    type: str
    default_price: float
    stock_quantity: int = 0
    active: bool = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    default_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
