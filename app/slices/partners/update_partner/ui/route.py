from fastapi import APIRouter, Depends
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.partners.update_partner.application.use_case import UpdatePartner
from app.slices.partners.update_partner.infra.repository import UpdatePartnerRepository
from .schemas import PartnerResponse, PartnerUpdate

router = APIRouter()

use_case = UpdatePartner(UpdatePartnerRepository())

@router.put("/{partner_id}", response_model=PartnerResponse)
async def route(partner_id: UUID, data: PartnerUpdate, current_user=Depends(get_current_user)):
    return await use_case.execute(
        partner_id=partner_id,
        name=data.name,
        active=data.active,
    )
