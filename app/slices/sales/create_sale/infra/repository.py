from typing import List, Optional
from uuid import UUID
from app.shared.db.models import Sale, SaleItem, SalePayment, PartnerCustomer, Product, Stock


class CreateSaleRepository:
    async def createSale(
        self,
        sale_code: str,
        total_amount: float,
        user_id: UUID,
        partner_id: Optional[UUID],
        items: list,
        payments: list,
        notes: Optional[str],
        observations: Optional[str],
        partner_customer_shift: Optional[str] = None,
        partner_customer_quantity: Optional[int] = None
    ):
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
        if partner_id and partner_customer_shift and partner_customer_quantity:
           await PartnerCustomer.create(partner_id = partner_id,
                                   sale_id = sale.id,
                                   quantity= partner_customer_quantity,
                                   shift= partner_customer_shift)
        return await Sale.get(id=sale.id).prefetch_related("items", "payments", "user")

    async def update_product_stock(self, stock: Stock):
              await Stock.create(product=stock.product, reason=stock.reason,
                                 change_type=stock.change_type,
                                 user=stock.user, quantity_change=stock.quantity_change, sale=stock.sale)
              update_data = {"stock_quantity": stock.product.stock_quantity}
              await Product.update_from_dict(stock.product, update_data).save()




