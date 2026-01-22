from fastapi import APIRouter

from app.slices.partners.create_partner.application.use_case import CreatePartner
from app.slices.partners.create_partner.infra.repository import CreatePartnerRepository
from app.slices.partners.create_partner.ui.schemas import PartnerResponse, PartnerCreate

router = APIRouter()

use_case = CreatePartner(CreatePartnerRepository())

@router.get("/", response_model=PartnerResponse)
async def route(data: PartnerCreate):
    return await use_case.execute(name=data.name, active=data.active)