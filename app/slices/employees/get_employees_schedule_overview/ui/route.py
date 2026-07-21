from fastapi import APIRouter, Depends, Query
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.employees.get_employees_schedule_overview.application.use_case import GetEmployeesScheduleOverview
from app.slices.employees.get_employees_schedule_overview.infra.repository import (
    GetEmployeesScheduleOverviewRepository,
)
from .schemas import EmployeeScheduleOverviewResponse
from app.shared.security.permissions import ensure_hr_or_admin

router = APIRouter(prefix="/schedule-overview")

use_case = GetEmployeesScheduleOverview(GetEmployeesScheduleOverviewRepository())


@router.get("", response_model=EmployeeScheduleOverviewResponse)
async def route(
    employee_ids: list[UUID] | None = Query(None),
    month: int | None = None,
    year: int | None = None,
    current_user=Depends(get_current_user),
):
    ensure_hr_or_admin(current_user)
    items = await use_case.execute(employee_ids=employee_ids, month=month, year=year)
    return EmployeeScheduleOverviewResponse(items=items)
