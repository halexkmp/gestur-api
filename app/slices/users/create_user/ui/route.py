from fastapi import APIRouter, Depends
from app.layers.auth import get_current_user
from app.slices.users.ui.schemas import UserCreate, UserResponse
from ..application.handler import create_user

router = APIRouter()

@router.post("", response_model=UserResponse, status_code=201)
async def route(user_in: UserCreate, current_user = Depends(get_current_user)):
    return await create_user(user_in)
