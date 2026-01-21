from uuid import UUID
from app.layers.db.models import Sale

async def get_sale(sale_id: UUID):
    return await Sale.get(id=sale_id).prefetch_related("items", "payments")
