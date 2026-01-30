from typing import Optional
from uuid import UUID
from app.shared.db.models import User
from app.shared.db.enums import UserRole

class UpdateUserRepository:
    async def update(
        self,
        user_id: UUID,
        name: Optional[str] = None,
        username: Optional[str] = None,
        password_hash: Optional[str] = None,
        role: Optional[UserRole] = None,
        active: Optional[bool] = None
    ) -> Optional[User]:
        user = await User.get_or_none(id=user_id)
        if not user:
            return None
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if username is not None:
            update_data["username"] = username
        if password_hash is not None:
            update_data["password_hash"] = password_hash
        if role is not None:
            update_data["role"] = role
        if active is not None:
            update_data["active"] = active
        if update_data:
            await user.update_from_dict(update_data).save()
        return user
