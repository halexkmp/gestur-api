from uuid import UUID
from app.slices.partners.delete_partner.infra.repository import DeletePartnerRepository

class DeletePartner:
    def __init__(self, repository: DeletePartnerRepository):
        self.repository = repository

    async def execute(self, partner_id: UUID):
        return await self.repository.delete(partner_id)
