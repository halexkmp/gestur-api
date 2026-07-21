from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.security.current_user import get_current_user
from app.slices.employees.create_justified_absence.application.use_case import CreateJustifiedAbsence
from app.slices.employees.create_justified_absence.infra.repository import CreateJustifiedAbsenceRepository
from .schemas import CreateJustifiedAbsenceRequest
from app.shared.security.permissions import ensure_hr_or_admin

router = APIRouter()

use_case = CreateJustifiedAbsence(CreateJustifiedAbsenceRepository())


@router.post("/justified-absences", status_code=status.HTTP_201_CREATED)
async def route(data: CreateJustifiedAbsenceRequest, current_user=Depends(get_current_user)):
    ensure_hr_or_admin(current_user)
    try:
        await use_case.execute(
            employee_id=data.employee_id,
            absence_date=data.absence_date,
            reason=data.reason,
        )
    except ValueError as e:
        err_msg = str(e)
        if "not found" in err_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
