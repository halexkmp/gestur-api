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
        # You can't set backward relations (items, payments) through init in Tortoise ORM.
        # Create the Sale first, then create SaleItem and SalePayment rows linking by sale_id.
        async with in_transaction():
            sale = await Sale.create(
                sale_code=sale_code,
                total_amount=total_amount,
                partner_id=partner_id,
                user_id=user_id,
                notes=notes,
                observations=observations,
            )
            # Create items
            for it in items or []:
                total_price = it["quantity"] * it["unit_price"]
                await SaleItem.create(
                    sale_id=sale.id,
                    product_id=it["product_id"],
                    quantity=it["quantity"],
                    unit_price=it["unit_price"],
                    total_price=total_price,
                )
            # Create payments
            for p in payments or []:
                await SalePayment.create(
                    sale_id=sale.id,
                    payment_method=p["payment_method"],
                    amount=p["amount"],
                )
        # Return sale with related items and payments
        return await Sale.get(id=sale.id).prefetch_related("items", "payments")



