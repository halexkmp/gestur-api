from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.shared.db.models import Sale


class FilterSalesRepository:
    async def filter(
        self,
        *,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        user_id: Optional[UUID] = None,
        product_id: Optional[UUID] = None,
        partner_id: Optional[UUID] = None,
    ) -> List[Sale]:
        query = Sale.all()
        if date_from is not None:
            query = query.filter(created_at__gte=date_from)
        if date_to is not None:
            query = query.filter(created_at__lte=date_to)
        if user_id is not None:
            query = query.filter(user_id=user_id)
        if partner_id is not None:
            query = query.filter(partner_id=partner_id)
        if product_id is not None:
            # Filter through related SaleItem
            query = query.filter(items__product_id=product_id)
        # Avoid duplicates when filtering via relation
        query = query.distinct()
        return await query.prefetch_related("items", "payments", "user").order_by("-created_at")
