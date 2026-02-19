from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.security.current_user import get_current_user
from app.slices.employees.create_salary_advance.application.use_case import CreateSalaryAdvance
from app.slices.employees.create_salary_advance.infra.repository import CreateSalaryAdvanceRepository
from .schemas import CreateSalaryAdvanceRequest, SalaryAdvanceResponse
from app.shared.security.permissions import ensure_hr

router = APIRouter(prefix="/salary-advances")

use_case = CreateSalaryAdvance(CreateSalaryAdvanceRepository())

@router.post("", response_model=SalaryAdvanceResponse, status_code=status.HTTP_201_CREATED)
async def route(data: CreateSalaryAdvanceRequest, current_user=Depends(get_current_user)):
    ensure_hr(current_user)
    try:
        return await use_case.execute(
            employee_id=data.employee_id,
            amount=float(data.amount),
            paid_at=data.paid_at,
            note=data.note,
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
