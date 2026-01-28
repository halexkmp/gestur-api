from datetime import datetime
from typing import Optional
from uuid import UUID
from app.shared.db.enums import UserRole
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
        current_user_id: UUID,
        current_user_role: str
    ):
        return await self.repository.filter(
            date_from=date_from,
            date_to=date_to,
            user_id= current_user_id if current_user_role == UserRole.OPERATOR else user_id,
            product_id=product_id,
            partner_id=partner_id,
        )
