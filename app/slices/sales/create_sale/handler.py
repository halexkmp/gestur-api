from app.slices.sales.ui.schemas import SaleCreate
from tortoise.transactions import in_transaction
from app.layers.db.models import Sale, SaleItem, SalePayment, Product, BugueiroClient

async def create_sale(data: SaleCreate, user_id):
    async with in_transaction():
        total_amount = 0
        for item in data.items:
            total_amount += item.quantity * item.unit_price

        last_sale = await Sale.all().order_by("-sale_number").first()
        sale_number = (last_sale.sale_number + 1) if last_sale else 1

        sale = await Sale.create(
            sale_number=sale_number,
            total_amount=total_amount,
            bugueiro_id=data.bugueiro_id,
            partner_id=data.partner_id,
            user_id=user_id,
            notes=data.notes,
            observations=data.observations
        )

        for item_data in data.items:
            product = await Product.get(id=item_data.product_id)
            await SaleItem.create(
                sale=sale,
                product=product,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                total_price=item_data.quantity * item_data.unit_price
            )
            if product.has_stock:
                product.stock_quantity -= item_data.quantity
                await product.save()

        for payment_data in data.payments:
            await SalePayment.create(
                sale=sale,
                payment_method=payment_data.payment_method,
                amount=payment_data.amount,
            )

        if data.bugueiro_id and data.bugueiro_client_date and data.bugueiro_client_shift:
            await BugueiroClient.create(
                bugueiro_id=data.bugueiro_id,
                sale=sale,
                client_date=data.bugueiro_client_date,
                shift=data.bugueiro_client_shift
            )

        return await Sale.get(id=sale.id).prefetch_related("items", "payments")
