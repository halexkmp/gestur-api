from uuid import UUID
from typing import Optional
from app.shared.db.models import JourneyRegistry

class DeleteJourneyRepository:
    async def get_by_id(self, journey_id: UUID) -> Optional[JourneyRegistry]:
        return await JourneyRegistry.get_or_none(id=journey_id)

    async def soft_delete(self, journey: JourneyRegistry) -> None:
        journey.is_deleted = True
        await journey.save()
