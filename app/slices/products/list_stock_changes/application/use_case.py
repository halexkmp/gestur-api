from typing import List, Optional
from uuid import UUID
from app.slices.products.list_stock_changes.infra.repository import ListStockChangesRepository


class ListStockChanges:
    def __init__(self, repository: ListStockChangesRepository):
        self.repository = repository

    async def execute(self, product_id: Optional[UUID] = None):
        return await self.repository.list(product_id=product_id)
