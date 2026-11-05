from fastapi import APIRouter, Depends

from app.shared.security.device_auth import get_current_device
from app.slices.tirolesa.device_heartbeat.application.use_case import DeviceHeartbeat
from .schemas import HeartbeatResponse

router = APIRouter()

use_case = DeviceHeartbeat()


@router.post("/devices/heartbeat", response_model=HeartbeatResponse)
async def route(device=Depends(get_current_device)):
    return HeartbeatResponse(server_time=use_case.execute())
