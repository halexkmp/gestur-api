from uuid import UUID

from fastapi import APIRouter, Depends
from typing import List, Optional
from app.shared.security.current_user import get_current_user
from app.slices.employees.list_justified_absences.application.use_case import ListJustifiedAbsences
from app.slices.employees.list_justified_absences.infra.repository import ListJustifiedAbsencesRepository
from .schemas import JustifiedAbsenceItem
from app.shared.security.permissions import ensure_hr_or_admin

router = APIRouter()
use_case = ListJustifiedAbsences(ListJustifiedAbsencesRepository())

@router.get("/justified-absences", response_model=List[JustifiedAbsenceItem])
async def route(
    employee_id: Optional[UUID] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user=Depends(get_current_user),
):
    ensure_hr_or_admin(current_user)
    return await use_case.execute(
        employee_id=employee_id,
        month=month,
        year=year,
    )
