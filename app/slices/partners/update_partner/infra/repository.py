from typing import Optional
from uuid import UUID
from app.shared.db.models import Partner

class UpdatePartnerRepository:
    async def update(
        self,
        partner_id: UUID,
        name: Optional[str] = None,
        active: Optional[bool] = None,
        pix_key: Optional[str] = None,
    ) -> Optional[Partner]:
        partner = await Partner.get_or_none(id=partner_id)
        if not partner:
            return None
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if active is not None:
            update_data["active"] = active
        if pix_key is not None:
            update_data["pix_key"] = pix_key
        if update_data:
            await partner.update_from_dict(update_data).save()
        return partner
