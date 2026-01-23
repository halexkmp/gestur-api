from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.slices.auth.login_user.application.use_case import LoginUser
from app.slices.auth.login_user.infra.password_hash_verifier import PasswordVerifyHash
from app.slices.auth.login_user.infra.repository import LoginUserRepository
from app.slices.auth.login_user.infra.token_service_creator import TokenService
from app.slices.auth.login_user.ui.schemas import TokenResponse

router = APIRouter()

use_case = LoginUser(LoginUserRepository(), PasswordVerifyHash(), TokenService())

@router.post("/login", response_model=TokenResponse)
async def route(form_data: OAuth2PasswordRequestForm = Depends()):
    return await use_case.execute(form_data.username, password=form_data.password)
