from uuid import UUID
from app.slices.journey.register_journey.infra.repository import RegisterJourneyRepository
from app.shared.db.models import JourneyRegistry

class RegisterJourney:
    def __init__(self, repository: RegisterJourneyRepository):
        self.repository = repository

    async def execute(self, user_id: UUID, latitude: float, longitude: float) -> JourneyRegistry:
        # Business logic could go here (e.g., checking if user is allowed to register)
        return await self.repository.create(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude
        )
