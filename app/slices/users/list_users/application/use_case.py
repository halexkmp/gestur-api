from typing import List

from app.shared.db.enums import UserRole
from app.slices.users.list_users.infra.repository import ListUsersRepository
from app.slices.users.list_users.ui.schemas import UserResponse


class ListUsers:
    def __init__(self, repository: ListUsersRepository):
        self.repository = repository

    async def execute(self, current_user: UserResponse) -> List[UserResponse]:
        return await self.repository.list() if current_user.role == UserRole.ADMIN else [current_user]
