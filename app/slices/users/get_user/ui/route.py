from fastapi import APIRouter, Depends
from uuid import UUID
from app.shared.security.current_password import get_current_user
from app.slices.users.get_user.application.use_case import GetUser
from app.slices.users.get_user.infra.repository import GetUserRepository
from .schemas import UserResponse

router = APIRouter()

use_case = GetUser(GetUserRepository())

@router.get("/{user_id}", response_model=UserResponse)
async def route(user_id: UUID, current_user=Depends(get_current_user)):
    return await use_case.execute(user_id)
