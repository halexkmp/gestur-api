from uuid import UUID
from app.shared.db.models import Product

class DeleteProductRepository:
    async def delete(self, product_id: UUID) -> bool:
        product = await Product.get_or_none(id=product_id)
        if not product:
            return False
        await product.delete()
        return True
