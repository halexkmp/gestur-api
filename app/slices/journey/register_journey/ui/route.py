from fastapi import APIRouter, Depends
from app.shared.security.current_user import get_current_user
from app.slices.journey.register_journey.ui.schemas import RegisterJourneyRequest, JourneyResponse
from app.slices.journey.register_journey.application.use_case import RegisterJourney
from app.slices.journey.register_journey.infra.repository import RegisterJourneyRepository
from app.shared.db.models import User

router = APIRouter()

use_case = RegisterJourney(RegisterJourneyRepository())

@router.post("/", response_model=JourneyResponse, status_code=201)
async def route(data: RegisterJourneyRequest, current_user: User = Depends(get_current_user)):
    return await use_case.execute(
        user_id=current_user.id,
        latitude=data.latitude,
        longitude=data.longitude
    )
