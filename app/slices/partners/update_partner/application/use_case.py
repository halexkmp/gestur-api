from typing import Optional
from uuid import UUID
from app.slices.partners.update_partner.infra.repository import UpdatePartnerRepository

class UpdatePartner:
    def __init__(self, repository: UpdatePartnerRepository):
        self.repository = repository

    async def execute(
        self,
        partner_id: UUID,
        pix_key: Optional[str] = None,
        name: Optional[str] = None,
        active: Optional[bool] = None,
    ):
        return await self.repository.update(
            partner_id=partner_id,
            pix_key=pix_key,
            name=name,
            active=active,
        )
