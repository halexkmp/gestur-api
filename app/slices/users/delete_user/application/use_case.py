from uuid import UUID
from app.slices.users.delete_user.infra.repository import DeleteUserRepository

class DeleteUser:
    def __init__(self, repository: DeleteUserRepository):
        self.repository = repository

    async def execute(self, user_id: UUID):
        return await self.repository.delete(user_id)
