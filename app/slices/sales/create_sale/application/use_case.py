from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from app.slices.sales.create_sale.infra.repository import CreateSaleRepository

class CreateSale:
    def __init__(self, repository: CreateSaleRepository):
        self.repository = repository

    async def execute(
        self,
        user_id: UUID,
        partner_id: Optional[UUID],
        items: list,
        payments: list,
        notes: Optional[str],
        observations: Optional[str],
    ):
        total_amount = sum(
            item.quantity * item.unit_price for item in items
        )

        sale_code = "{}{}".format(user_id, datetime.now().strftime("%Y%m%d%H%M%S"))

        return await self.repository.create(
            sale_code=sale_code,
            total_amount=total_amount,
            user_id=user_id,
            partner_id=partner_id,
            items=items,
            payments=payments,
            notes=notes,
            observations=observations,
        )

