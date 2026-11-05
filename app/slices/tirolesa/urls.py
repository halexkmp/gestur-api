from fastapi import APIRouter
from app.slices.tirolesa.create_device.ui.route import router as create_device
from app.slices.tirolesa.list_devices.ui.route import router as list_devices
from app.slices.tirolesa.update_device.ui.route import router as update_device

router = APIRouter(prefix="/tirolesa", tags=["tirolesa"])
router.include_router(create_device)
router.include_router(list_devices)
router.include_router(update_device)
