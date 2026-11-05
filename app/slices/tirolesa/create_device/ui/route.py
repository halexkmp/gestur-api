from fastapi import APIRouter, Depends, status

from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import ensure_admin_or_manager
from app.slices.tirolesa.create_device.application.use_case import CreateDevice
from app.slices.tirolesa.create_device.infra.repository import CreateDeviceRepository
from .schemas import CreateDeviceRequest, CreateDeviceResponse

router = APIRouter()

use_case = CreateDevice(CreateDeviceRepository())


@router.post("/devices", response_model=CreateDeviceResponse, status_code=status.HTTP_201_CREATED)
async def route(data: CreateDeviceRequest, current_user=Depends(get_current_user)):
    ensure_admin_or_manager(current_user)
    device, api_key = await use_case.execute(name=data.name)
    return CreateDeviceResponse(
        id=device.id,
        name=device.name,
        active=device.active,
        created_at=device.created_at,
        api_key=api_key,
    )
