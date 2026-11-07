from uuid import UUID

from pydantic import BaseModel, Field


class LinkProductRequest(BaseModel):
    product_id: UUID
    passengers_per_unit: int = Field(default=1, ge=1)


class LinkProductResponse(BaseModel):
    id: UUID
    product_id: UUID
    passengers_per_unit: int
