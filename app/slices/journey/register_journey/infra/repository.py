from typing import Optional
from uuid import UUID
from datetime import datetime, time
from app.shared.db.models import JourneyRegistry

class RegisterJourneyRepository:
    async def create(self, user_id: UUID, latitude: float, longitude: float) -> JourneyRegistry:
        return await JourneyRegistry.create(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude
        )

    async def count_today_by_user(self, user_id: UUID) -> int:
        today_start = datetime.combine(datetime.utcnow().date(), time.min)
        today_end = datetime.combine(datetime.utcnow().date(), time.max)
        return await JourneyRegistry.filter(
            user_id=user_id,
            timestamp__range=(today_start, today_end),
            is_deleted=False
        ).count()

    async def get_last_by_user(self, user_id: UUID) -> Optional[JourneyRegistry]:
        return await JourneyRegistry.filter(
            user_id=user_id,
            is_deleted=False
        ).order_by("-timestamp").first()
