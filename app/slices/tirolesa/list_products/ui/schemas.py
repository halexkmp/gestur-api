from uuid import UUID

from pydantic import BaseModel


class TirolesaProductResponse(BaseModel):
    id: UUID
    product_id: UUID
    product_name: str
    passengers_per_unit: int
