from uuid import UUID
from app.shared.db.models import Partner

class DeletePartnerRepository:
    async def delete(self, partner_id: UUID) -> bool:
        partner = await Partner.get_or_none(id=partner_id)
        if not partner:
            return False
        await partner.delete()
        return True
