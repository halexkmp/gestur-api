from fastapi import APIRouter, Depends
from typing import List
from app.shared.security.current_user import get_current_user
from app.slices.partners.list_partners.application.use_case import ListPartners
from app.slices.partners.list_partners.infra.repository import ListPartnersRepository
from .schemas import PartnerResponse

router = APIRouter()

use_case = ListPartners(ListPartnersRepository())

@router.get("/", response_model=List[PartnerResponse])
async def route(current_user=Depends(get_current_user)):
    return await use_case.execute()
