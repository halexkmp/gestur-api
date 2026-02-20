from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.security.current_user import get_current_user
from app.slices.employees.create_salary_advance.application.use_case import CreateSalaryAdvance
from app.slices.employees.create_salary_advance.infra.repository import CreateSalaryAdvanceRepository
from .schemas import CreateSalaryAdvanceRequest, SalaryAdvanceResponse
from app.shared.security.permissions import ensure_hr

router = APIRouter()

use_case = CreateSalaryAdvance(CreateSalaryAdvanceRepository())

@router.post("/salary-advances", response_model=SalaryAdvanceResponse, status_code=status.HTTP_201_CREATED)
async def route(data: CreateSalaryAdvanceRequest, current_user=Depends(get_current_user)):
    ensure_hr(current_user)
    try:
        return await use_case.execute(
            employee_id=data.employee_id,
            amount=data.amount,
            note=data.note,
        )
    except ValueError as e:
        msg = str(e) if str(e) else "Invalid request"
        if msg == "Employee not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
