from typing import Optional
from uuid import UUID
from app.shared.db.enums import StockChangeType
from app.shared.db.models import Product, Sale, Stock, User


class UpdateStockRepository:
    async def update_stock(
        self,
        *,
        product_id: UUID,
        change_type: StockChangeType,
        quantity_change: int,
        user_id: UUID,
        sale_id: Optional[UUID] = None,
    ) -> Optional[Stock]:
        product = await Product.get_or_none(id=product_id)
        user = await User.get_or_none(id=user_id)
        sale = None
        if sale_id:
            sale = await Sale.get_or_none(id=sale_id)

        if not product or not user:
            return None

        magnitude = abs(quantity_change)
        delta = magnitude if change_type == StockChangeType.IN else -magnitude

        # Update product stock quantity
        product.stock_quantity = (product.stock_quantity or 0) + delta
        await product.save()

        # Create stock entry
        stock = await Stock.create(
            change_type=change_type,
            product=product,
            quantity_change=delta,
            sale=sale,
            user=user,
        )
        return stock
