from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import resolve_own_employee_id
from app.slices.employees.get_my_employee_schedule.application.use_case import GetMyEmployeeSchedule
from app.slices.employees.get_my_employee_schedule.infra.repository import GetMyEmployeeScheduleRepository
from .schemas import EmployeeScheduleResponse

router = APIRouter()

use_case = GetMyEmployeeSchedule(GetMyEmployeeScheduleRepository())


@router.get("/me/schedule", response_model=EmployeeScheduleResponse)
async def route(current_user=Depends(get_current_user)):
    employee_id = resolve_own_employee_id(current_user)
    try:
        return await use_case.execute(employee_id=employee_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
