from fastapi import APIRouter
from app.slices.journey.register_journey.ui.route import router as register_router
from app.slices.journey.list_my_journeys.ui.route import router as list_my_router
from app.slices.journey.admin_list_journeys.ui.route import router as admin_list_router
from app.slices.journey.update_journey.ui.route import router as update_router
from app.slices.journey.delete_journey.ui.route import router as delete_router

router = APIRouter(prefix="/journey", tags=["Journey"])

router.include_router(register_router)
router.include_router(list_my_router)
router.include_router(admin_list_router)
router.include_router(update_router)
router.include_router(delete_router)
