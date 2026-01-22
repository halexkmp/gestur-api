from typing import List
from app.shared.db.models import Sale
from app.slices.sales.list_sales.infra.repository import ListSalesRepository

class ListSales:
    def __init__(self, repository: ListSalesRepository):
        self.repository = repository

    async def execute(self) -> List[Sale]:
        return await self.repository.list()
