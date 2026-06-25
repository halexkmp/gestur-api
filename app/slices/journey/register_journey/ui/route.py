from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from app.shared.security.current_user import get_current_user
from app.slices.journey.register_journey.ui.schemas import JourneyResponse
from app.slices.journey.register_journey.application.use_case import RegisterJourney, MaxRecordsReachedError, MinimumIntervalError
from app.slices.journey.register_journey.infra.repository import RegisterJourneyRepository
from app.shared.db.models import User

router = APIRouter()

use_case = RegisterJourney(RegisterJourneyRepository())

@router.post("/", response_model=JourneyResponse, status_code=201)
async def route(
    latitude: float = Form(...),
    longitude: float = Form(...),
    selfie: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    try:
        selfie_content = await selfie.read()
        return await use_case.execute(
            user_id=current_user.id,
            latitude=latitude,
            longitude=longitude,
            selfie_file=selfie_content
        )
    except MaxRecordsReachedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MinimumIntervalError as e:
        raise HTTPException(status_code=400, detail=str(e))
