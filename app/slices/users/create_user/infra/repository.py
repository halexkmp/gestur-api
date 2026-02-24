from typing import List
from app.shared.db.models import User, Role
from app.shared.db.enums import UserRole

class CreateUserRepository:

    async def create(self, name: str, username: str, password_hash: str, roles: List[UserRole]) -> User:
        user = await User.create(
            name=name,
            username=username,
            password_hash=password_hash,
        )
        # Ensure Role entries exist and link them
        role_objs = []
        for r in roles:
            role_obj, _ = await Role.get_or_create(name=r)
            role_objs.append(role_obj)
        await user.roles.add(*role_objs)
        return user
