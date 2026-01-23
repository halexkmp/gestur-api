from uuid import UUID
from app.shared.db.models import User

class DeleteUserRepository:
    async def delete(self, user_id: UUID) -> bool:
        user = await User.get_or_none(id=user_id)
        if not user:
            return False
        await user.delete()
        return True
