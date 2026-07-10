from typing import List
from app.shared.db.models import Partner
from app.shared.db.enums import PartnerType


class ListPartnersByTypeRepository:
    async def list_by_type(self, type: PartnerType) -> List[Partner]:
        return await Partner.filter(type=type).prefetch_related('loans').all()
