from fastapi import APIRouter, Depends
from typing import List, Optional
from app.shared.security.current_user import get_current_user
from app.slices.employees.list_salary_advances.application.use_case import ListSalaryAdvances
from app.slices.employees.list_salary_advances.infra.repository import ListSalaryAdvancesRepository
from .schemas import SalaryAdvanceItem
from app.shared.security.permissions import ensure_hr

router = APIRouter()
use_case = ListSalaryAdvances(ListSalaryAdvancesRepository())

@router.get("/salary-advances", response_model=List[SalaryAdvanceItem])
async def route(
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user=Depends(get_current_user),
):
    ensure_hr(current_user)
    return await use_case.execute(
        month=month,
        year=year,
    )
