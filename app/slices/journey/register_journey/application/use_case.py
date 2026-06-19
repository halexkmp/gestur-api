from uuid import UUID
from datetime import datetime, timedelta
from app.slices.journey.register_journey.infra.repository import RegisterJourneyRepository
from app.shared.db.models import JourneyRegistry

class MaxRecordsReachedError(Exception):
    pass

class MinimumIntervalError(Exception):
    pass

class RegisterJourney:
    def __init__(self, repository: RegisterJourneyRepository):
        self.repository = repository

    async def execute(self, user_id: UUID, latitude: float, longitude: float) -> JourneyRegistry:
        # Rule: Max 4 records per day
        count = await self.repository.count_today_by_user(user_id)
        if count >= 4:
            raise MaxRecordsReachedError("Maximum of 4 records per day reached")

        # Rule: Min 1-minute interval
        last_record = await self.repository.get_last_by_user(user_id)
        if last_record:
            # last_record.timestamp is expected to be UTC
            now = datetime.utcnow()
            # Tortoise DatetimeField usually returns timezone-aware datetimes if configured, 
            # but let's assume naive UTC for consistency if not specified otherwise in project
            # Actually, good practice is to compare offset-aware or both naive.
            # If last_record.timestamp is aware, now should be too.
            
            diff = now - last_record.timestamp.replace(tzinfo=None) # Ensure naive for comparison with datetime.utcnow()
            if diff < timedelta(minutes=1):
                raise MinimumIntervalError("Minimum 1-minute interval required between records")

        return await self.repository.create(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude
        )
