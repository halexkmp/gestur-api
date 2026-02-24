from typing import List
from fastapi import APIRouter, Depends, status
from app.shared.security.current_user import get_current_user
from app.slices.employees.create_salary_advance.application.use_case import CreateSalaryAdvance
from app.slices.employees.create_salary_advance.infra.repository import CreateSalaryAdvanceRepository
from .schemas import CreateSalaryAdvanceRequest
from app.shared.security.permissions import ensure_hr

router = APIRouter()

use_case = CreateSalaryAdvance(CreateSalaryAdvanceRepository())

@router.post("/salary-advances", status_code=status.HTTP_201_CREATED)
async def route(data: CreateSalaryAdvanceRequest, current_user=Depends(get_current_user)):
    ensure_hr(current_user)

    await use_case.execute(
        employee_id=data.employee_id,
        amount=data.amount,
        advance_date=data.advance_date,
        note=data.note,
        times=data.times,
    )

