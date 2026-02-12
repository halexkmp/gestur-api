from fastapi import APIRouter
from app.slices.permissions.list_roles.ui.route import router as list_roles_router

router = APIRouter(prefix="/permissions", tags=["permissions"])
router.include_router(list_roles_router)
