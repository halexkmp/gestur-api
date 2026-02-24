from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.employees.get_salary_summary.application.use_case import GetSalarySummary
from app.slices.employees.get_salary_summary.infra.repository import GetSalarySummaryRepository
from .schemas import SalarySummaryResponse
from app.shared.security.permissions import ensure_hr

router = APIRouter(prefix="/salary-summary")

use_case = GetSalarySummary(GetSalarySummaryRepository())


@router.get("/{employee_id}", response_model=SalarySummaryResponse)
async def route(
    employee_id: UUID,
    month: int | None = None,
    year: int | None = None,
    current_user=Depends(get_current_user),
):
    ensure_hr(current_user)
    try:
        return await use_case.execute(
            employee_id=employee_id,
            month=month,
            year=year,
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
