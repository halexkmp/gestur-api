from uuid import UUID
from typing import List, Optional
from datetime import datetime
from app.slices.journey.admin_list_journeys.infra.repository import AdminListJourneysRepository
from app.shared.db.models import JourneyRegistry

class AdminListJourneys:
    def __init__(self, repository: AdminListJourneysRepository):
        self.repository = repository

    async def execute(
        self,
        user_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[JourneyRegistry]:
        return await self.repository.list_journeys(user_id, start_date, end_date)
