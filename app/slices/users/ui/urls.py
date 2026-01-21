from fastapi import APIRouter
from app.slices.users.create_user.ui.route import router as create_router
from app.slices.users.get_me.ui.route import router as me_router

router = APIRouter(prefix="/users", tags=["users"])
router.include_router(create_router)
router.include_router(me_router, prefix="/me")
