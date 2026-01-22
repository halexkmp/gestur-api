from app.slices.partners.create_partner.infra.repository import CreatePartnerRepository

class CreatePartner:
    def __init__(self, repository: CreatePartnerRepository):
        self.repository = repository

    async def execute(self, name: str, active: bool = True):
        return await self.repository.create(name=name, active=active)
