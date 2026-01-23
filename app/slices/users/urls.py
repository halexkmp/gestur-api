from fastapi import APIRouter
from app.slices.users.create_user.ui.route import router as create_router
from app.slices.users.get_me.ui.route import router as me_router
from app.slices.users.list_users.ui.route import router as list_users
from app.slices.users.get_user.ui.route import router as get_user
from app.slices.users.update_user.ui.route import router as update_user
from app.slices.users.delete_user.ui.route import router as delete_user

router = APIRouter(prefix="/users", tags=["users"])
router.include_router(create_router)
router.include_router(me_router)
router.include_router(list_users)
router.include_router(get_user)
router.include_router(update_user)
router.include_router(delete_user)
