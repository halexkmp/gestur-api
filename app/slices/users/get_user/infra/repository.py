from typing import Optional
from uuid import UUID
from app.shared.db.models import User

class GetUserRepository:
    async def get(self, user_id: UUID) -> Optional[User]:
        return await User.get_or_none(id=user_id)
