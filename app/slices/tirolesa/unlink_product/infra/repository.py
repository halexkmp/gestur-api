from uuid import UUID

from app.shared.db.models import TirolesaProduct


class UnlinkProductRepository:
    async def delete(self, tirolesa_product_id: UUID) -> bool:
        deleted = await TirolesaProduct.filter(id=tirolesa_product_id).delete()
        return deleted > 0
