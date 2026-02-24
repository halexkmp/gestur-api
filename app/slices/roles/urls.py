from fastapi import APIRouter
from app.slices.roles.list_roles.ui.route import router as list_roles_router

router = APIRouter(prefix="/roles", tags=["roles"])
router.include_router(list_roles_router)
