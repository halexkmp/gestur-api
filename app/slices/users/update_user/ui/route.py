from fastapi import APIRouter, Depends
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.users.update_user.application.use_case import UpdateUser
from app.slices.users.update_user.infra.repository import UpdateUserRepository
from app.slices.users.create_user.infra.password_hash_create import PasswordHashCreate
from .schemas import UserResponse, UserUpdate

router = APIRouter()

use_case = UpdateUser(UpdateUserRepository(), PasswordHashCreate())

@router.put("/{user_id}", response_model=UserResponse)
async def route(user_id: UUID, user_in: UserUpdate, current_user=Depends(get_current_user)):
    return await use_case.execute(
        user_id=user_id,
        name=user_in.name,
        username=user_in.username,
        password=user_in.password,
        roles=user_in.roles,
        active=user_in.active
    )
