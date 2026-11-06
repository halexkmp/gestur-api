from fastapi import APIRouter, Depends

from app.shared.security.cron_auth import verify_cron_secret
from app.slices.tirolesa.check_offline_devices.application.use_case import CheckOfflineDevices
from app.slices.tirolesa.check_offline_devices.infra.repository import CheckOfflineDevicesRepository
from .schemas import CheckOfflineDevicesResponse

router = APIRouter()

use_case = CheckOfflineDevices(CheckOfflineDevicesRepository())


@router.post(
    "/devices/check-offline",
    response_model=CheckOfflineDevicesResponse,
    dependencies=[Depends(verify_cron_secret)],
)
async def route():
    return CheckOfflineDevicesResponse(marked_offline=await use_case.execute())
