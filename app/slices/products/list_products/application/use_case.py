from typing import List
from app.shared.db.models import Product
from app.slices.products.list_products.infra.repository import ListProductsRepository

class ListProducts:
    def __init__(self, repository: ListProductsRepository):
        self.repository = repository

    async def execute(self) -> List[Product]:
        return await self.repository.list()
