from typing import List
from uuid import UUID
from app.shared.db.models import PartnerCustomer
from app.slices.reports.get_partner_customers_by_sales.infra.repository import (
    GetPartnerCustomersBySalesRepository,
)


class GetPartnerCustomersBySales:
    def __init__(self, repository: GetPartnerCustomersBySalesRepository):
        self.repository = repository

    async def execute(self, *, sale_ids: List[UUID]) -> List[PartnerCustomer]:
        return await self.repository.by_sales(sale_ids=sale_ids)
