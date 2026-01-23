from typing import Optional
from uuid import UUID
from app.shared.db.models import Partner

class GetPartnerRepository:
    async def get(self, partner_id: UUID) -> Optional[Partner]:
        return await Partner.get_or_none(id=partner_id)
