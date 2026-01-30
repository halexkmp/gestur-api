from fastapi import APIRouter, Depends
from app.shared.security.current_user import get_current_user
from app.slices.users.create_user.infra.password_hash_create import PasswordHashCreate
from app.slices.users.create_user.ui.schemas import UserCreate, UserResponse
from app.slices.users.create_user.application.use_case import CreateUser
from app.slices.users.create_user.infra.repository import CreateUserRepository

router = APIRouter()

use_case = CreateUser(CreateUserRepository(), PasswordHashCreate())

@router.post("/", response_model=UserResponse, status_code=201)
async def route(user_in: UserCreate, current_user=Depends(get_current_user)):
    return await use_case.execute(
        name=user_in.name,
        username=user_in.username,
        password=user_in.password,
        role=user_in.role,
    )
