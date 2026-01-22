from app.shared.auth import get_password_hash
from app.slices.users.create_user.infra.repository import CreateUserRepository
from app.shared.db.enums import UserRole

class CreateUser:
    def __init__(self, repository: CreateUserRepository):
        self.repository = repository

    async def execute(self, name: str, username: str, password: str, role: UserRole):
        password_hash = get_password_hash(password)
        return await self.repository.create(
            name=name,
            email=username,
            password_hash=password_hash,
            role=role,
        )
