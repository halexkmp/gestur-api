from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import resolve_own_employee_id
from app.slices.employees.get_my_salary_summary.application.use_case import GetMySalarySummary
from app.slices.employees.get_my_salary_summary.infra.repository import GetMySalarySummaryRepository
from .schemas import SalarySummaryResponse

router = APIRouter()

use_case = GetMySalarySummary(GetMySalarySummaryRepository())


@router.get("/me/salary-summary", response_model=SalarySummaryResponse)
async def route(
    month: int | None = None,
    year: int | None = None,
    current_user=Depends(get_current_user),
):
    employee_id = resolve_own_employee_id(current_user)
    try:
        return await use_case.execute(
            employee_id=employee_id,
            month=month,
            year=year,
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
