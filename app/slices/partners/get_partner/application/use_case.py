from uuid import UUID
from app.slices.partners.get_partner.infra.repository import GetPartnerRepository

class GetPartner:
    def __init__(self, repository: GetPartnerRepository):
        self.repository = repository

    async def execute(self, partner_id: UUID):
        return await self.repository.get(partner_id)
