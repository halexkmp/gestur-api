from fastapi import APIRouter, Depends
from app.shared.auth import get_current_user
from .schemas import UserResponse

router = APIRouter()

@router.get("", response_model=UserResponse)
async def route(current_user = Depends(get_current_user)):
    return current_user
