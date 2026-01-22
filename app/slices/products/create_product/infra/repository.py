from app.shared.db.models import Product

class CreateProductRepository:
    async def create(
        self,
        name: str,
        type: str,
        default_price: float,
        has_stock: bool,
        stock_quantity: int,
        active: bool,
    ):
        return await Product.create(
            name=name,
            type=type,
            default_price=default_price,
            has_stock=has_stock,
            stock_quantity=stock_quantity,
            active=active,
        )
