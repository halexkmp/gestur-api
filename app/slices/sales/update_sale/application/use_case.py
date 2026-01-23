from typing import List, Optional
from uuid import UUID
from app.slices.sales.update_sale.infra.repository import UpdateSaleRepository
from app.shared.db.enums import SaleStatus


class UpdateSale:
    def __init__(self, repository: UpdateSaleRepository):
        self.repository = repository

    async def execute(
        self,
        sale_id: UUID,
        partner_id: Optional[UUID] = None,
        status: Optional[SaleStatus] = None,
        notes: Optional[str] = None,
        observations: Optional[str] = None,
        items: Optional[list] = None,
        payments: Optional[list] = None,
        modified_by: Optional[str] = None,
    ):
        # If items provided, compute total from them; otherwise keep existing total
        total_amount: Optional[float] = None
        if items is not None:
            total_amount = sum(item.quantity * item.unit_price for item in items)

        return await self.repository.update(
            sale_id=sale_id,
            partner_id=partner_id,
            status=status,
            notes=notes,
            observations=observations,
            items=items,
            payments=payments,
            total_amount=total_amount,
            modified_by=modified_by,
        )
