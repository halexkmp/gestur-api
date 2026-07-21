from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.employees.get_attendance_verification.application.use_case import GetAttendanceVerification
from app.slices.employees.get_attendance_verification.infra.repository import GetAttendanceVerificationRepository
from .schemas import AttendanceVerificationResponse
from app.shared.security.permissions import ensure_hr_or_admin

router = APIRouter(prefix="/attendance-verification")

use_case = GetAttendanceVerification(GetAttendanceVerificationRepository())


@router.get("/{employee_id}", response_model=AttendanceVerificationResponse)
async def route(
    employee_id: UUID,
    month: int | None = None,
    year: int | None = None,
    current_user=Depends(get_current_user),
):
    ensure_hr_or_admin(current_user)
    try:
        return await use_case.execute(
            employee_id=employee_id,
            month=month,
            year=year,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
