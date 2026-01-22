from typing import Optional
from uuid import UUID
from app.shared.db.models import Product

class UpdateProductRepository:
    async def update(
        self,
        product_id: UUID,
        name: Optional[str] = None,
        type: Optional[str] = None,
        default_price: Optional[float] = None,
        has_stock: Optional[bool] = None,
        stock_quantity: Optional[int] = None,
        active: Optional[bool] = None,
    ) -> Optional[Product]:
        product = await Product.get_or_none(id=product_id)
        if not product:
            return None
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if type is not None:
            update_data["type"] = type
        if default_price is not None:
            update_data["default_price"] = default_price
        if has_stock is not None:
            update_data["has_stock"] = has_stock
        if stock_quantity is not None:
            update_data["stock_quantity"] = stock_quantity
        if active is not None:
            update_data["active"] = active
        if update_data:
            await product.update_from_dict(update_data).save()
        return product
