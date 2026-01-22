from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.slices.auth.login_user.ui.schemas import TokenResponse
from app.slices.auth.login_user.application.use_case import login

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def route(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login(form_data)
