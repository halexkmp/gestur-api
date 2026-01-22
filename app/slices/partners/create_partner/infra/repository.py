from app.shared.db.models import Partner

class CreatePartnerRepository:
    async def create(self, name: str, active: bool = True):
        return await Partner.create(name=name, active=active)
