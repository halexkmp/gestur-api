from uuid import UUID

from app.shared.db.models import Product, TirolesaProduct


class LinkProductRepository:
    async def product_exists(self, product_id: UUID) -> bool:
        return await Product.filter(id=product_id).exists()

    async def is_linked(self, product_id: UUID) -> bool:
        return await TirolesaProduct.filter(product_id=product_id).exists()

    async def create(self, product_id: UUID, passengers_per_unit: int) -> TirolesaProduct:
        return await TirolesaProduct.create(product_id=product_id, passengers_per_unit=passengers_per_unit)
