from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.security.current_user import get_current_user
from app.slices.employees.update_lateness_config.application.use_case import UpdateLatenessConfiguration
from app.slices.employees.update_lateness_config.infra.repository import UpdateLatenessConfigurationRepository
from .schemas import UpdateLatenessConfigRequest, LatenessConfigResponse
from app.shared.security.permissions import ensure_hr

router = APIRouter()

use_case = UpdateLatenessConfiguration(UpdateLatenessConfigurationRepository())


@router.put("/lateness-config", response_model=LatenessConfigResponse)
async def route(data: UpdateLatenessConfigRequest, current_user=Depends(get_current_user)):
    ensure_hr(current_user)
    try:
        return await use_case.execute(
            enabled=data.enabled,
            expected_entrance_time=data.expected_entrance_time,
            tolerance_minutes=data.tolerance_minutes,
            deduction_interval_minutes=data.deduction_interval_minutes,
            deduction_value=data.deduction_value,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
