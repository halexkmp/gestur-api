from typing import List
from app.shared.db.models import Role


class ListRolesRepository:
    async def list(self) -> List[Role]:
        return await Role.all().order_by("name")
