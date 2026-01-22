from uuid import UUID
from app.slices.sales.get_sale.infra.repository import GetSaleRepository

class GetSale:
    def __init__(self, repository: GetSaleRepository):
        self.repository = repository

    async def execute(self, sale_id: UUID):
        return await self.repository.get(sale_id)
