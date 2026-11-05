from fastapi import APIRouter
from app.slices.tirolesa.create_device.ui.route import router as create_device
from app.slices.tirolesa.list_devices.ui.route import router as list_devices
from app.slices.tirolesa.update_device.ui.route import router as update_device
from app.slices.tirolesa.record_trip.ui.route import router as record_trip
from app.slices.tirolesa.device_heartbeat.ui.route import router as device_heartbeat
from app.slices.tirolesa.link_product.ui.route import router as link_product
from app.slices.tirolesa.list_products.ui.route import router as list_products
from app.slices.tirolesa.unlink_product.ui.route import router as unlink_product
from app.slices.tirolesa.create_justification.ui.route import router as create_justification
from app.slices.tirolesa.delete_justification.ui.route import router as delete_justification
from app.slices.tirolesa.get_daily_audit.ui.route import router as get_daily_audit

router = APIRouter(prefix="/tirolesa", tags=["tirolesa"])
router.include_router(create_device)
router.include_router(list_devices)
router.include_router(update_device)
router.include_router(record_trip)
router.include_router(device_heartbeat)
router.include_router(link_product)
router.include_router(list_products)
router.include_router(unlink_product)
router.include_router(create_justification)
router.include_router(delete_justification)
router.include_router(get_daily_audit)
