from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import ensure_hr_or_admin
from app.slices.employees.delete_justified_absence.application.use_case import DeleteJustifiedAbsence
from app.slices.employees.delete_justified_absence.infra.repository import DeleteJustifiedAbsenceRepository

router = APIRouter()
use_case = DeleteJustifiedAbsence(DeleteJustifiedAbsenceRepository())

@router.delete("/justified-absences/{absence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route(absence_id: UUID, current_user=Depends(get_current_user)):
    ensure_hr_or_admin(current_user)
    deleted = await use_case.execute(absence_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Justified absence not found")
    return None
