from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from fastapi import HTTPException, status
from app.shared.auth import verify_password, create_access_token
from app.shared.db.models import User
from app.config import settings

async def login(form_data: OAuth2PasswordRequestForm):
    user = await User.get_or_none(email=form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
