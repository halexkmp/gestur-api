from app.shared.db.models import Partner

class CreatePartnerRepository:
    async def create(self, name: str, type: str, active: bool = True, pix_key: str = None):
        return await Partner.create(name=name, type=type, active=active, pix_key=pix_key)
