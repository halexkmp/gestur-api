from typing import List
from uuid import UUID
from app.shared.db.models import PartnerCustomer


class GetPartnerCustomersBySalesRepository:
    async def by_sales(self, *, sale_ids: List[UUID]) -> List[PartnerCustomer]:
        if not sale_ids:
            return []
        # Fetch partner customers linked to any of the provided sale IDs
        return await PartnerCustomer.filter(sale_id__in=sale_ids).all()
