from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.employees.get_employee_schedule.application.use_case import GetEmployeeSchedule
from app.slices.employees.get_employee_schedule.infra.repository import GetEmployeeScheduleRepository
from .schemas import EmployeeScheduleResponse
from app.shared.security.permissions import ensure_hr_or_admin

router = APIRouter(prefix="/schedule")

use_case = GetEmployeeSchedule(GetEmployeeScheduleRepository())


@router.get("/{employee_id}", response_model=EmployeeScheduleResponse)
async def route(employee_id: UUID, current_user=Depends(get_current_user)):
    ensure_hr_or_admin(current_user)
    try:
        return await use_case.execute(employee_id=employee_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
