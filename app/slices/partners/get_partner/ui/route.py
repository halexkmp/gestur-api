from fastapi import APIRouter, Depends
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.partners.get_partner.application.use_case import GetPartner
from app.slices.partners.get_partner.infra.repository import GetPartnerRepository
from .schemas import PartnerResponse

router = APIRouter()

use_case = GetPartner(GetPartnerRepository())

@router.get("/{partner_id}", response_model=PartnerResponse)
async def route(partner_id: UUID, current_user=Depends(get_current_user)):
    return await use_case.execute(partner_id)
