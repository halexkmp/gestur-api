from typing import Optional
from uuid import UUID
from app.shared.db.enums import StockChangeType
from app.slices.products.update_stock.infra.repository import UpdateStockRepository


class UpdateStock:
    def __init__(self, repository: UpdateStockRepository):
        self.repository = repository

    async def execute(
        self,
        *,
        product_id: UUID,
        change_type: StockChangeType,
        quantity_change: int,
        user_id: UUID,
        sale_id: Optional[UUID] = None,
        reason: Optional[str] = None
    ):
        return await self.repository.update_stock(
            product_id=product_id,
            change_type=change_type,
            quantity_change=quantity_change,
            user_id=user_id,
            sale_id=sale_id,
            reason=reason
        )
