from uuid import UUID
from fastapi import HTTPException
from typing import Optional
from app.slices.products.update_product.infra.repository import UpdateProductRepository

class UpdateProduct:
    def __init__(self, repository: UpdateProductRepository):
        self.repository = repository

    async def execute(
        self,
        product_id: UUID,
        name: Optional[str] = None,
        type: Optional[str] = None,
        default_price: Optional[float] = None,
        has_stock: Optional[bool] = None,
        stock_quantity: Optional[int] = None,
        active: Optional[bool] = None,
    ):
        product = await self.repository.update(
            product_id=product_id,
            name=name,
            type=type,
            default_price=default_price,
            has_stock=has_stock,
            stock_quantity=stock_quantity,
            active=active,
        )
        return product
