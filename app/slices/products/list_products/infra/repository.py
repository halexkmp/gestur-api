from typing import List
from app.shared.db.models import Product

class ListProductsRepository:
    async def list(self) -> List[Product]:
        return await Product.all()
