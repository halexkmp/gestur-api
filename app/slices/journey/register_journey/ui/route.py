from fastapi import APIRouter, Depends, HTTPException
from app.shared.security.current_user import get_current_user
from app.slices.journey.register_journey.ui.schemas import RegisterJourneyRequest, JourneyResponse
from app.slices.journey.register_journey.application.use_case import RegisterJourney, MaxRecordsReachedError, MinimumIntervalError
from app.slices.journey.register_journey.infra.repository import RegisterJourneyRepository
from app.shared.db.models import User

router = APIRouter()

use_case = RegisterJourney(RegisterJourneyRepository())

@router.post("/", response_model=JourneyResponse, status_code=201)
async def route(data: RegisterJourneyRequest, current_user: User = Depends(get_current_user)):
    try:
        return await use_case.execute(
            user_id=current_user.id,
            latitude=data.latitude,
            longitude=data.longitude
        )
    except MaxRecordsReachedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MinimumIntervalError as e:
        raise HTTPException(status_code=400, detail=str(e))
