from typing import List
from app.slices.users.create_user.infra.password_hash_create import PasswordHashCreate
from app.slices.users.create_user.infra.repository import CreateUserRepository
from app.shared.db.enums import UserRole

class CreateUser:
    def __init__(self, repository: CreateUserRepository, password_hash_creator: PasswordHashCreate):
        self.repository = repository
        self.password_hash_creator = password_hash_creator

    async def execute(self, name: str, username: str, password: str, roles: List[UserRole]):
        password_hash = self.password_hash_creator.get_password_hash(password)
        user = await self.repository.create(
            name=name,
            username=username,
            password_hash=password_hash,
            roles=roles,
        )
        # Build response dict including roles
        await user.fetch_related("roles")
        return {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "roles": [r.name for r in user.roles],
            "created_at": user.created_at,
        }
