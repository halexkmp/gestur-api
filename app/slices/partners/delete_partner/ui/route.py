from fastapi import APIRouter, Depends
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.partners.delete_partner.application.use_case import DeletePartner
from app.slices.partners.delete_partner.infra.repository import DeletePartnerRepository

router = APIRouter()

use_case = DeletePartner(DeletePartnerRepository())

@router.delete("/{partner_id}")
async def route(partner_id: UUID, current_user=Depends(get_current_user)):
    return await use_case.execute(partner_id)
