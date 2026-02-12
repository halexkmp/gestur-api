from fastapi import APIRouter, Depends
from typing import List

from app.shared.security.current_user import get_current_user
from app.slices.permissions.list_roles.application.use_case import ListRoles
from app.slices.permissions.list_roles.infra.repository import ListRolesRepository
from .schemas import RoleResponse

router = APIRouter()

use_case = ListRoles(ListRolesRepository())

@router.get("/roles", response_model=List[RoleResponse])
async def route(current_user=Depends(get_current_user)):
    return await use_case.execute()
