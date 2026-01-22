from typing import List
from app.shared.db.models import Sale

class ListSalesRepository:
    async def list(self) -> List[Sale]:
        return await Sale.all().prefetch_related("items", "payments")
