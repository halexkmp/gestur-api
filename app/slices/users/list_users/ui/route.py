from fastapi import APIRouter, Depends
from typing import List
from app.shared.security.current_user import get_current_user
from app.slices.users.list_users.application.use_case import ListUsers
from app.slices.users.list_users.infra.repository import ListUsersRepository
from .schemas import UserResponse

router = APIRouter()

use_case = ListUsers(ListUsersRepository())

@router.get("/", response_model=List[UserResponse])
async def route(current_user=Depends(get_current_user)):
    return await use_case.execute(current_user)
