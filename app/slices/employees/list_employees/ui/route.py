from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.shared.security.current_user import get_current_user
from app.slices.employees.list_employees.application.use_case import ListEmployees
from app.slices.employees.list_employees.infra.repository import ListEmployeesRepository
from .schemas import EmployeeResponse
from app.shared.security.permissions import ensure_hr

router = APIRouter()

use_case = ListEmployees(ListEmployeesRepository())


@router.get("/", response_model=List[EmployeeResponse])
async def route(active: Optional[bool] = None, current_user=Depends(get_current_user)):
    ensure_hr(current_user)
    return await use_case.execute(active=active)
