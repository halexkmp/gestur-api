from fastapi import APIRouter, Depends
from typing import List, Optional
from datetime import datetime
from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import ensure_admin
from app.slices.journey.register_journey.ui.schemas import JourneyResponse
from app.slices.journey.admin_list_journeys.application.use_case import AdminListJourneys
from app.slices.journey.admin_list_journeys.infra.repository import AdminListJourneysRepository
from uuid import UUID

router = APIRouter()

use_case = AdminListJourneys(AdminListJourneysRepository())

@router.get("/admin", response_model=List[JourneyResponse])
async def route(
    user_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user = Depends(get_current_user)
):
    ensure_admin(current_user)
    return await use_case.execute(user_id, start_date, end_date)
