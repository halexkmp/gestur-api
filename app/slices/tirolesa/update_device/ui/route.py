from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import ensure_admin_or_manager
from app.slices.tirolesa.update_device.application.use_case import UpdateDevice
from app.slices.tirolesa.update_device.infra.repository import UpdateDeviceRepository
from .schemas import UpdateDeviceRequest, UpdateDeviceResponse

router = APIRouter()

use_case = UpdateDevice(UpdateDeviceRepository())


@router.put("/devices/{device_id}", response_model=UpdateDeviceResponse)
async def route(device_id: UUID, data: UpdateDeviceRequest, current_user=Depends(get_current_user)):
    ensure_admin_or_manager(current_user)
    try:
        device = await use_case.execute(device_id=device_id, name=data.name, active=data.active)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return UpdateDeviceResponse(
        id=device.id,
        name=device.name,
        active=device.active,
        last_seen_at=device.last_seen_at,
    )
