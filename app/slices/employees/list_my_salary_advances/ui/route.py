from typing import List, Optional

from fastapi import APIRouter, Depends
from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import resolve_own_employee_id
from app.slices.employees.list_my_salary_advances.application.use_case import ListMyAdvances
from app.slices.employees.list_my_salary_advances.infra.repository import ListMyAdvancesRepository
from .schemas import SalaryAdvanceItem

router = APIRouter()
use_case = ListMyAdvances(ListMyAdvancesRepository())


@router.get("/me/salary-advances", response_model=List[SalaryAdvanceItem])
async def route(
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user=Depends(get_current_user),
):
    employee_id = resolve_own_employee_id(current_user)
    return await use_case.execute(
        employee_id=employee_id,
        month=month,
        year=year,
    )
