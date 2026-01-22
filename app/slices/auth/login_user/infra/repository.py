from app.shared.db.models import User


class LoginUserRepository:
    async def get_user(self, username: str):
        await User.get_or_none(email=username)