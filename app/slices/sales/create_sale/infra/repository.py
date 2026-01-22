from typing import List, Optional
from uuid import UUID
from datetime import date
from tortoise.transactions import in_transaction
from app.shared.db.models import Sale, SaleItem, SalePayment, Product, PartnerCustomer
from app.shared.db.enums import PartnerCustomerShift

class CreateSaleRepository:
    async def create(
        self,
        sale_code: str,
        total_amount: float,
        user_id: UUID,
        partner_id: Optional[UUID],
        items: list,
        payments: list,
        notes: Optional[str],
        observations: Optional[str],
    ):
       async with in_transaction():
            return await Sale.create(
                sale_code=sale_code,
                total_amount=total_amount,
                partner_id=partner_id,
                user_id=user_id,
                notes=notes,
                observations=observations,
                items=items,
                payments=payments,
            )



