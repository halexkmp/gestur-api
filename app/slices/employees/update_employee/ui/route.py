from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.employees.update_employee.application.use_case import UpdateEmployee
from app.slices.employees.update_employee.infra.repository import UpdateEmployeeRepository
from .schemas import EmployeeUpdate, EmployeeResponse
from app.shared.security.permissions import ensure_hr

router = APIRouter()

use_case = UpdateEmployee(UpdateEmployeeRepository())


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def route(employee_id: UUID, data: EmployeeUpdate, current_user=Depends(get_current_user)):
    ensure_hr(current_user)
    try:
        return await use_case.execute(
            employee_id=employee_id,
            name=data.name,
            pix_key=data.pix_key,
            salary=data.salary,
            active=data.active,
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
