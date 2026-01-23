from typing import List
from app.shared.db.models import User
from app.slices.users.list_users.infra.repository import ListUsersRepository

class ListUsers:
    def __init__(self, repository: ListUsersRepository):
        self.repository = repository

    async def execute(self) -> List[User]:
        return await self.repository.list()
