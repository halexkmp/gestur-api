from fastapi import APIRouter, Depends, Query
from typing import List
from app.shared.security.current_password import get_current_user
from app.shared.db.enums import PartnerType
from app.slices.partners.list_partners_by_type.application.use_case import ListPartnersByType
from app.slices.partners.list_partners_by_type.infra.repository import ListPartnersByTypeRepository
from .schemas import PartnerResponse

router = APIRouter()

use_case = ListPartnersByType(ListPartnersByTypeRepository())


@router.get("/by-type", response_model=List[PartnerResponse])
async def route(type: PartnerType = Query(...), current_user=Depends(get_current_user)):
    return await use_case.execute(type=type)
