from app.shared.db.models import Partner
from app.partners.schema import PartnerCreate

async def create_partner(data: PartnerCreate):
    return await Partner.create(**data.model_dump())
