from uuid import UUID, uuid4
from datetime import datetime, timedelta
from app.slices.journey.register_journey.infra.repository import RegisterJourneyRepository
from app.shared.infra.image_service import ImageService
from app.shared.db.models import JourneyRegistry

class MaxRecordsReachedError(Exception):
    pass

class MinimumIntervalError(Exception):
    pass

class RegisterJourney:
    def __init__(self, repository: RegisterJourneyRepository, image_service: ImageService = None):
        self.repository = repository
        self.image_service = image_service or ImageService()

    async def execute(self, user_id: UUID, latitude: float, longitude: float, selfie_file: bytes = None) -> JourneyRegistry:
        # Rule: Max 4 records per day
        count = await self.repository.count_today_by_user(user_id)
        if count >= 4:
            raise MaxRecordsReachedError("Maximum of 4 records per day reached")

        # Rule: Min 1-minute interval
        last_record = await self.repository.get_last_by_user(user_id)
        if last_record:
            # last_record.timestamp is expected to be UTC
            now = datetime.utcnow()
            
            diff = now - last_record.timestamp.replace(tzinfo=None) # Ensure naive for comparison with datetime.utcnow()
            if diff < timedelta(minutes=1):
                raise MinimumIntervalError("Minimum 1-minute interval required between records")

        selfie_id = None
        if selfie_file:
            optimized_selfie = self.image_service.optimize_image(selfie_file)
            filename = f"{user_id}_{uuid4()}.jpg"
            selfie_id = await self.image_service.upload_selfie(optimized_selfie, filename)

        return await self.repository.create(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            selfie_id=selfie_id
        )
