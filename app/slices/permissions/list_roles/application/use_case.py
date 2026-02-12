from typing import List
from app.slices.permissions.list_roles.infra.repository import ListRolesRepository


class ListRoles:
    def __init__(self, repository: ListRolesRepository):
        self.repository = repository

    async def execute(self):
        return await self.repository.list()
