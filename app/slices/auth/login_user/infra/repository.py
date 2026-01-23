from app.shared.db.models import User


class LoginUserRepository:
   async def get_user(self, username: str):
        return await User.get_or_none(username=username)