from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.employees.delete_employee.application.use_case import DeleteEmployee
from app.slices.employees.delete_employee.infra.repository import DeleteEmployeeRepository
from app.shared.security.permissions import ensure_hr

router = APIRouter()

use_case = DeleteEmployee(DeleteEmployeeRepository())


@router.delete("/{employee_id}", status_code=204)
async def route(employee_id: UUID, current_user=Depends(get_current_user)):
    ensure_hr(current_user)
    ok = await use_case.execute(employee_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return None
