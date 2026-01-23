from fastapi import APIRouter
from app.slices.auth.login_user.ui.route import router as login_router

router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(login_router)