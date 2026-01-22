from uuid import UUID
from fastapi import HTTPException
from app.slices.products.delete_product.infra.repository import DeleteProductRepository

class DeleteProduct:
    def __init__(self, repository: DeleteProductRepository):
        self.repository = repository

    async def execute(self, product_id: UUID):
        return await self.repository.delete(product_id)