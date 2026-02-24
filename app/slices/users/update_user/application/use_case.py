from typing import Optional, List
from uuid import UUID
from app.slices.users.update_user.infra.repository import UpdateUserRepository
from app.slices.users.create_user.infra.password_hash_create import PasswordHashCreate
from app.slices.users.update_user.ui.schemas import RoleUpdate


class UpdateUser:
    def __init__(self, repository: UpdateUserRepository, password_hash_creator: PasswordHashCreate):
        self.repository = repository
        self.password_hash_creator = password_hash_creator

    async def execute(
        self,
        user_id: UUID,
        name: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        roles: Optional[List[RoleUpdate]] = None,
        active: Optional[bool] = None
    ):
        password_hash = None
        if password is not None:
            password_hash = self.password_hash_creator.get_password_hash(password)
        return await self.repository.update(
            user_id=user_id,
            name=name,
            username=username,
            password_hash=password_hash,
            roles=roles,
            active=active
        )
