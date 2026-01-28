from typing import List, Optional
from uuid import UUID
from app.shared.db.models import Stock


class ListStockChangesRepository:
    async def list(self, product_id: Optional[UUID] = None) -> List[Stock]:
        query = Stock.all()
        if product_id:
            query = query.filter(product_id=product_id)
        return (
            await query
            .prefetch_related("product", "sale", "user")
            .order_by("-created_at")
        )
