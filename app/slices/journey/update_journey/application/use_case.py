from uuid import UUID
from typing import Optional
from datetime import datetime
from app.slices.journey.update_journey.infra.repository import UpdateJourneyRepository
from app.shared.db.models import JourneyRegistry

class JourneyNotFoundError(Exception):
    pass

class UpdateJourney:
    def __init__(self, repository: UpdateJourneyRepository):
        self.repository = repository

    async def execute(
        self,
        journey_id: UUID,
        latitude: Optional[float],
        longitude: Optional[float],
        timestamp: Optional[datetime],
        edit_reason: str
    ) -> JourneyRegistry:
        journey = await self.repository.get_by_id(journey_id)
        if not journey:
            raise JourneyNotFoundError()

        # Save original data for auditing if it's the first time it's edited
        if not journey.original_data:
            original_data = {
                "latitude": journey.latitude,
                "longitude": journey.longitude,
                "timestamp": journey.timestamp.isoformat() if journey.timestamp else None
            }
        else:
            original_data = journey.original_data

        return await self.repository.update(
            journey=journey,
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
            edit_reason=edit_reason,
            original_data=original_data
        )
