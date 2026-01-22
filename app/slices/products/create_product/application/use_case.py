from app.slices.products.create_product.infra.repository import CreateProductRepository
class CreateProduct:
    def __init__(self, repository: CreateProductRepository):
        self.repository = repository

    async def execute(
        self,
        name: str,
        type: str,
        default_price: float,
        has_stock: bool,
        stock_quantity: int,
        active: bool,
    ):
        return await self.repository.create(
            name=name,
            type=type,
            default_price=default_price,
            has_stock=has_stock,
            stock_quantity=stock_quantity,
            active=active,
        )
