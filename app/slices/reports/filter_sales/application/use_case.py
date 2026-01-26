from datetime import datetime
from typing import List, Optional
from uuid import UUID
from app.shared.db.models import Sale
from app.slices.reports.filter_sales.infra.repository import FilterSalesRepository


class FilterSales:
    def __init__(self, repository: FilterSalesRepository):
        self.repository = repository

    async def execute(
        self,
        *,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        user_id: Optional[UUID] = None,
        product_id: Optional[UUID] = None,
        partner_id: Optional[UUID] = None,
    ) -> List[Sale]:
        return await self.repository.filter(
            date_from=date_from,
            date_to=date_to,
            user_id=user_id,
            product_id=product_id,
            partner_id=partner_id,
        )
