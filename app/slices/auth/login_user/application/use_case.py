from datetime import timedelta
from app.config import settings
from app.slices.auth.login_user.infra.password_hash_verifier import PasswordVerifyHash
from app.slices.auth.login_user.infra.repository import LoginUserRepository
from app.slices.auth.login_user.infra.token_service_creator import TokenService

class LoginUser:
    def __init__(self, repository: LoginUserRepository, verifier: PasswordVerifyHash, token_service: TokenService):
        self.verifier = verifier
        self.token_service = token_service
        self.repository = repository

    async def execute(self, username: str, password: str):
        user = await self.repository.get_user("hpaiva")
        if not user or not self.verifier.verify_hash_password(password, user.password_hash):
            raise Exception("Invalid credentials")
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.token_service.create_access_token(data={"username": user.username, "id":user.id}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}

