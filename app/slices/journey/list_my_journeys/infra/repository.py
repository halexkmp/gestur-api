from uuid import UUID
from typing import List
from app.shared.db.models import JourneyRegistry

class ListMyJourneysRepository:
    async def list_by_user(self, user_id: UUID) -> List[JourneyRegistry]:
        return await JourneyRegistry.filter(
            user_id=user_id,
            is_deleted=False
        ).order_by("-timestamp")
