from app.slices.users.create_user.ui.schemas import UserCreate, UserResponse
from app.shared.db.models import User
from app.shared.auth import get_password_hash
from fastapi import HTTPException, status

async def create_user(data: UserCreate) -> UserResponse:
    existing_user = await User.get_or_none(email=data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    user = await User.create(
        name=data.name,
        email=data.email,
        password_hash=get_password_hash(data.password),
        role=data.role
    )
    return user
