from app.shared.db.models import User
from app.shared.db.enums import UserRole

class CreateUserRepository:

    async def create(self, name: str, username: str, password_hash: str, role: UserRole) -> User:
        return await User.create(
            name=name,
            username=username,
            password_hash=password_hash,
            role=role,
        )
