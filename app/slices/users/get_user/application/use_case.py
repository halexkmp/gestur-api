from uuid import UUID
from app.slices.users.get_user.infra.repository import GetUserRepository

class GetUser:
    def __init__(self, repository: GetUserRepository):
        self.repository = repository

    async def execute(self, user_id: UUID):
        return await self.repository.get(user_id)
