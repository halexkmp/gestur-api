from typing import List
from app.shared.db.models import User

class ListUsersRepository:
    async def list(self) -> List[User]:
        return await User.all()
