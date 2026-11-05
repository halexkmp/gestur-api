from typing import List

from app.shared.db.models import TirolesaProduct


class ListProductsRepository:
    async def list(self) -> List[TirolesaProduct]:
        return await TirolesaProduct.all().prefetch_related("product").order_by("created_at")
