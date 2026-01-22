from uuid import UUID
from typing import Optional
from app.shared.db.models import Product

class GetProductRepository:
    async def get(self, product_id: UUID) -> Optional[Product]:
        return await Product.get_or_none(id=product_id)
