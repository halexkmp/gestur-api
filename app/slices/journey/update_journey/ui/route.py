from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import ensure_admin
from app.slices.journey.register_journey.ui.schemas import JourneyResponse
from app.slices.journey.update_journey.ui.schemas import UpdateJourneyRequest
from app.slices.journey.update_journey.application.use_case import UpdateJourney, JourneyNotFoundError
from app.slices.journey.update_journey.infra.repository import UpdateJourneyRepository

router = APIRouter()

use_case = UpdateJourney(UpdateJourneyRepository())

@router.patch("/{journey_id}", response_model=JourneyResponse)
async def route(
    journey_id: UUID,
    data: UpdateJourneyRequest,
    current_user = Depends(get_current_user)
):
    ensure_admin(current_user)
    try:
        return await use_case.execute(
            journey_id=journey_id,
            latitude=data.latitude,
            longitude=data.longitude,
            timestamp=data.timestamp,
            edit_reason=data.edit_reason
        )
    except JourneyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journey not found")
