from app.slices.partners.create_partner.infra.repository import CreatePartnerRepository

class CreatePartner:
    def __init__(self, repository: CreatePartnerRepository):
        self.repository = repository

    async def execute(self, name: str, type: str, active: bool = True, pix_key: str = None):
        return await self.repository.create(name=name, type=type, active=active, pix_key=pix_key)
