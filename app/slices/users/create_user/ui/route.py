from fastapi import APIRouter, Depends
from app.shared.auth import get_current_user
from .schemas import UserCreate, UserResponse
from ..application.use_case import create_user

router = APIRouter()

@router.post("", response_model=UserResponse, status_code=201)
async def route(user_in: UserCreate, current_user = Depends(get_current_user)):
    return await create_user(user_in)
