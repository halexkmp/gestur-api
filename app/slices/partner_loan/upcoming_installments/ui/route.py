from fastapi import APIRouter, Depends, HTTPException, Query, status
from datetime import date
from typing import List, Optional
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.partner_loan.upcoming_installments.application.use_case import (
    ListUpcomingInstallments,
)
from app.slices.partner_loan.upcoming_installments.infra.repository import (
    UpcomingInstallmentsRepository,
)
from app.slices.partner_loan.upcoming_installments.ui.schemas import (
    UpcomingInstallmentResponse,
)

router = APIRouter()
use_case = ListUpcomingInstallments(UpcomingInstallmentsRepository())


@router.get("/upcoming-installments", response_model=List[UpcomingInstallmentResponse])
async def route(
    start_date: date = Query(...),
    end_date: date = Query(...),
    include_overdue: bool = Query(False),
    partner_id: Optional[UUID] = Query(None),
    limit: Optional[int] = Query(None, ge=1),
    current_user=Depends(get_current_user),
):
    try:
        return await use_case.execute(
            start_date=start_date,
            end_date=end_date,
            include_overdue=include_overdue,
            partner_id=partner_id,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
