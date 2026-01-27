from fastapi import APIRouter, Depends

from app.shared.security.current_password import get_current_user
from app.slices.partners.create_partner.application.use_case import CreatePartner
from app.slices.partners.create_partner.infra.repository import CreatePartnerRepository
from app.slices.partners.create_partner.ui.schemas import PartnerResponse, PartnerCreate

router = APIRouter()

use_case = CreatePartner(CreatePartnerRepository())

@router.post("/", response_model=PartnerResponse)
async def route(data: PartnerCreate, current_user=Depends(get_current_user)):
    return await use_case.execute(name=data.name, active=data.active, pix_key=data.pix_key)