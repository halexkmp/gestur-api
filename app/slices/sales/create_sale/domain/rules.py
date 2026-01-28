from app.shared.db.models import Product, Stock, Sale
from app.shared.db.enums import ProductType, StockChangeType


async def update_stock_by_sale(sale: Sale):

    await sale.fetch_related("items", "user")
    user = getattr(sale, "user", None)
    # Iterate over sale items and update stock for consumable products
    for it in getattr(sale, "items", []) or []:
        await it.fetch_related("product")
        product = getattr(it, "product", None)

        if product.type != ProductType.CONSUMABLE:
            continue
        qty = int(getattr(it, "quantity", 0) or 0)
        if qty <= 0:
            continue

        # Decrease product stock
        product.stock_quantity = (product.stock_quantity or 0) - qty
        await product.save()

        # Create a stock history entry (OUT)
        delta = -abs(qty)
        await Stock.create(
            change_type=StockChangeType.OUT,
            product=product,
            quantity_change=delta,
            sale=sale,
            user=user,
            reason=f"VENDA {sale.sale_code}"
        )

