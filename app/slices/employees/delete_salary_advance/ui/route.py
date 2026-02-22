from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import ensure_hr
from app.slices.employees.delete_salary_advance.application.use_case import DeleteSalaryAdvance
from app.slices.employees.delete_salary_advance.infra.repository import DeleteSalaryAdvanceRepository

router = APIRouter()
use_case = DeleteSalaryAdvance(DeleteSalaryAdvanceRepository())

@router.delete("/salary-advances/{advance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route(advance_id: UUID, current_user=Depends(get_current_user)):
    ensure_hr(current_user)
    deleted = await use_case.execute(advance_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salary advance not found")
    return None
