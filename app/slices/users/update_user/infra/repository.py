from typing import Optional, List
from uuid import UUID
from app.shared.db.models import User, Role

class UpdateUserRepository:
    async def update(
        self,
        user_id: UUID,
        name: Optional[str] = None,
        username: Optional[str] = None,
        password_hash: Optional[str] = None,
        roles: Optional[List[Role]] = None,
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
        if active is not None:
            update_data["active"] = active
        if update_data:
            await user.update_from_dict(update_data).save()
        if roles is not None:
            roles_instances = await Role.filter(id__in=[r.id for r in roles])
            await user.roles.clear()
            await user.roles.add(*roles_instances)
        await user.fetch_related("roles")
        return user
