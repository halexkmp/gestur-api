from datetime import datetime, timezone
from uuid import UUID

from app.slices.tirolesa.record_trip.domain.rules import is_clock_suspect
from app.slices.tirolesa.record_trip.infra.repository import RecordTripRepository


class RecordTrip:
    def __init__(self, repository: RecordTripRepository):
        self.repository = repository

    async def execute(
        self,
        device_id: UUID,
        trip_id: UUID,
        start: datetime,
        end: datetime,
        passengers: int,
    ) -> bool:
        now = datetime.now(timezone.utc)
        return await self.repository.create_if_new(
            trip_id=trip_id,
            device_id=device_id,
            start_at=start,
            end_at=end,
            passengers=passengers,
            clock_suspect=is_clock_suspect(start, end, now),
        )
