from uuid import UUID
from app.shared.db.models import Sale

class GetSaleRepository:
    async def get(self, sale_id: UUID):
        return await Sale.get(id=sale_id).prefetch_related("items", "payments")
