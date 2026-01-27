from app.shared.db.models import Partner

class CreatePartnerRepository:
    async def create(self, name: str, active: bool = True, pix_key: str = None):
        return await Partner.create(name=name, active=active, pix_key=pix_key)
