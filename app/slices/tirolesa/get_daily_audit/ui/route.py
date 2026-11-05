from dataclasses import asdict
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import ensure_admin_or_manager
from app.slices.tirolesa.get_daily_audit.application.use_case import GetDailyAudit
from app.slices.tirolesa.get_daily_audit.infra.repository import GetDailyAuditRepository
from .schemas import AuditDayResponse, AuditJustification, JustificationUser

router = APIRouter()

use_case = GetDailyAudit(GetDailyAuditRepository())


@router.get("/audit", response_model=List[AuditDayResponse])
async def route(
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user=Depends(get_current_user),
):
    ensure_admin_or_manager(current_user)
    try:
        days = await use_case.execute(date_from=date_from, date_to=date_to)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return [
        AuditDayResponse(
            date=day.date,
            **asdict(day.figures),
            justifications=[
                AuditJustification(
                    id=justification.id,
                    quantity=justification.quantity,
                    type=justification.type,
                    reason=justification.reason,
                    created_by=JustificationUser(
                        id=justification.created_by.id,
                        name=justification.created_by.name,
                    ),
                    created_at=justification.created_at,
                )
                for justification in day.justifications
            ],
        )
        for day in days
    ]
