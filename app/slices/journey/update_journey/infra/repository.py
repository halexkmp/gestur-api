from uuid import UUID
from typing import Optional
from datetime import datetime
from app.shared.db.models import JourneyRegistry

class UpdateJourneyRepository:
    async def get_by_id(self, journey_id: UUID) -> Optional[JourneyRegistry]:
        return await JourneyRegistry.get_or_none(id=journey_id)

    async def update(
        self,
        journey: JourneyRegistry,
        latitude: Optional[float],
        longitude: Optional[float],
        timestamp: Optional[datetime],
        edit_reason: str,
        original_data: dict
    ) -> JourneyRegistry:
        if latitude is not None:
            journey.latitude = latitude
        if longitude is not None:
            journey.longitude = longitude
        if timestamp is not None:
            journey.timestamp = timestamp
        
        journey.edit_reason = edit_reason
        journey.original_data = original_data
        
        await journey.save()
        return journey
