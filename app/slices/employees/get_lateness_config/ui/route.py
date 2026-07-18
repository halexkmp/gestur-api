from fastapi import APIRouter, Depends
from app.shared.security.current_user import get_current_user
from app.slices.employees.get_lateness_config.application.use_case import GetLatenessConfiguration
from app.slices.employees.get_lateness_config.infra.repository import GetLatenessConfigurationRepository
from .schemas import LatenessConfigResponse
from app.shared.security.permissions import ensure_hr

router = APIRouter()

use_case = GetLatenessConfiguration(GetLatenessConfigurationRepository())


@router.get("/lateness-config", response_model=LatenessConfigResponse)
async def route(current_user=Depends(get_current_user)):
    ensure_hr(current_user)
    return await use_case.execute()
