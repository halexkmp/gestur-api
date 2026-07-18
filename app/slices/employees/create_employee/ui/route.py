from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.security.current_user import get_current_user
from app.slices.employees.create_employee.application.use_case import CreateEmployee
from app.slices.employees.create_employee.infra.repository import CreateEmployeeRepository
from .schemas import CreateEmployeeRequest, EmployeeResponse
from app.shared.security.permissions import ensure_hr

router = APIRouter()

use_case = CreateEmployee(CreateEmployeeRepository())


@router.post("/", response_model=EmployeeResponse)
async def route(data: CreateEmployeeRequest, current_user=Depends(get_current_user)):
    ensure_hr(current_user)
    try:
        return await use_case.execute(
            name=data.name,
            pix_key=data.pix_key,
            salary=data.salary,
            active=data.active,
            start_date=data.start_date,
            user_id=data.user_id
        )
    except ValueError as e:
        err_msg = str(e)
        if "not found" in err_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
