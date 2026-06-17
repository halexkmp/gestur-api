from uuid import UUID
from typing import List
from app.slices.journey.list_my_journeys.infra.repository import ListMyJourneysRepository
from app.shared.db.models import JourneyRegistry

class ListMyJourneys:
    def __init__(self, repository: ListMyJourneysRepository):
        self.repository = repository

    async def execute(self, user_id: UUID) -> List[JourneyRegistry]:
        return await self.repository.list_by_user(user_id)
