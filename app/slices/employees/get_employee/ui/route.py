from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.employees.get_employee.application.use_case import GetEmployee
from app.slices.employees.get_employee.infra.repository import GetEmployeeRepository
from .schemas import EmployeeResponse
from app.shared.security.permissions import ensure_hr

router = APIRouter()

use_case = GetEmployee(GetEmployeeRepository())


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def route(employee_id: UUID, current_user=Depends(get_current_user)):
    ensure_hr(current_user)
    try:
        return await use_case.execute(employee_id=employee_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
