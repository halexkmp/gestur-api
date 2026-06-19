from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import ensure_admin
from app.slices.journey.delete_journey.application.use_case import DeleteJourney, JourneyNotFoundError
from app.slices.journey.delete_journey.infra.repository import DeleteJourneyRepository

router = APIRouter()

use_case = DeleteJourney(DeleteJourneyRepository())

@router.delete("/{journey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route(
    journey_id: UUID,
    current_user = Depends(get_current_user)
):
    ensure_admin(current_user)
    try:
        await use_case.execute(journey_id=journey_id)
    except JourneyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journey not found")
