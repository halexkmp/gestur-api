from uuid import UUID
from app.slices.journey.delete_journey.infra.repository import DeleteJourneyRepository

class JourneyNotFoundError(Exception):
    pass

class DeleteJourney:
    def __init__(self, repository: DeleteJourneyRepository):
        self.repository = repository

    async def execute(self, journey_id: UUID) -> None:
        journey = await self.repository.get_by_id(journey_id)
        if not journey:
            raise JourneyNotFoundError()
        
        await self.repository.soft_delete(journey)
