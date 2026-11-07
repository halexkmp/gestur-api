from datetime import datetime
from uuid import UUID

from tortoise.exceptions import IntegrityError

from app.shared.db.models import TirolesaTrip


class RecordTripRepository:
    async def create_if_new(
        self,
        trip_id: UUID,
        device_id: UUID,
        start_at: datetime,
        end_at: datetime,
        passengers: int,
        clock_suspect: bool,
    ) -> bool:
        """Return True when created. A repeated id is a resend, so it is not an error."""
        try:
            await TirolesaTrip.create(
                id=trip_id,
                device_id=device_id,
                start_at=start_at,
                end_at=end_at,
                passengers=passengers,
                clock_suspect=clock_suspect,
            )
        except IntegrityError:
            return False
        return True
