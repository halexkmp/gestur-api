from typing import Optional, List
from uuid import UUID
from tortoise.transactions import in_transaction
from app.shared.db.models import Sale, SaleItem, SalePayment
from app.shared.db.enums import SaleStatus, PaymentMethod


class UpdateSaleRepository:
    async def update(
        self,
        sale_id: UUID,
        partner_id: Optional[UUID] = None,
        status: Optional[SaleStatus] = None,
        notes: Optional[str] = None,
        observations: Optional[str] = None,
        items: Optional[list] = None,
        payments: Optional[list] = None,
        total_amount: Optional[float] = None,
        modified_by: Optional[str] = None,
    ):
        sale = await Sale.get_or_none(id=sale_id)
        if not sale:
            return None

        # Update scalar fields
        update_data = {}
        if partner_id is not None:
            update_data["partner_id"] = partner_id
        if status is not None:
            update_data["status"] = status
        if notes is not None:
            update_data["notes"] = notes
        if observations is not None:
            update_data["observations"] = observations
        if modified_by is not None:
            update_data["modified_by"] = modified_by
        if total_amount is not None:
            update_data["total_amount"] = total_amount

        # Apply simple updates first
        if update_data:
            await sale.update_from_dict(update_data).save()

        # If items or payments provided, we replace them atomically
        if items is not None or payments is not None:
            async with in_transaction():
                if items is not None:
                    # Delete existing items and recreate
                    await SaleItem.filter(sale_id=sale_id).delete()
                    for it in items:
                        # it expected to have product_id, quantity, unit_price, and we compute total_price here
                        total_price = it.quantity * it.unit_price
                        await SaleItem.create(
                            sale_id=sale_id,
                            product_id=it.product_id,
                            quantity=it.quantity,
                            unit_price=it.unit_price,
                            total_price=total_price,
                        )
                if payments is not None:
                    await SalePayment.filter(sale_id=sale_id).delete()
                    for p in payments:
                        await SalePayment.create(
                            sale_id=sale_id,
                            payment_method=p.payment_method,
                            amount=p.amount,
                        )
                # If total_amount not supplied (no items), keep as-is; otherwise already updated above
                if items is not None:
                    # recompute again to ensure consistency on DB side
                    total_amount_db = sum([it.quantity * it.unit_price for it in items])
                    await Sale.filter(id=sale_id).update(total_amount=total_amount_db)

        # Return updated sale with relations
        return await Sale.get(id=sale_id).prefetch_related("items", "payments")
