from uuid import UUID
from app.shared.db.models import JourneyRegistry

class RegisterJourneyRepository:
    async def create(self, user_id: UUID, latitude: float, longitude: float) -> JourneyRegistry:
        return await JourneyRegistry.create(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude
        )
