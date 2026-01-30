from app.shared.db.models import Stock, Sale
from app.shared.db.enums import ProductType, StockChangeType


async def update_stock_by_sale(sale: Sale):

    user = getattr(sale, "user", None)
    stock_changes = []
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

        # Create a stock history entry (OUT)
        delta = -abs(qty)
        stock_changes.append(Stock(
            change_type=StockChangeType.OUT,
            product=product,
            quantity_change=delta,
            sale=sale,
            user=user,
            reason=f"VENDA {sale.sale_code}"
        ))
    return stock_changes
