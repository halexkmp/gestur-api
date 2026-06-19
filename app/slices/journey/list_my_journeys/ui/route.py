from fastapi import APIRouter, Depends
from typing import List
from app.shared.security.current_user import get_current_user
from app.slices.journey.register_journey.ui.schemas import JourneyResponse
from app.slices.journey.list_my_journeys.application.use_case import ListMyJourneys
from app.slices.journey.list_my_journeys.infra.repository import ListMyJourneysRepository
from app.shared.db.models import User

router = APIRouter()

use_case = ListMyJourneys(ListMyJourneysRepository())

@router.get("/", response_model=List[JourneyResponse])
async def route(current_user: User = Depends(get_current_user)):
    return await use_case.execute(user_id=current_user.id)
