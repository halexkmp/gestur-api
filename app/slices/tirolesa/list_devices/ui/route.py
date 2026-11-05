from typing import List

from fastapi import APIRouter, Depends

from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import ensure_admin_or_manager
from app.slices.tirolesa.list_devices.application.use_case import ListDevices
from app.slices.tirolesa.list_devices.infra.repository import ListDevicesRepository
from .schemas import DeviceResponse

router = APIRouter()

use_case = ListDevices(ListDevicesRepository())


@router.get("/devices", response_model=List[DeviceResponse])
async def route(current_user=Depends(get_current_user)):
    ensure_admin_or_manager(current_user)
    return await use_case.execute()
