from fastapi import APIRouter, Depends, HTTPException, Query, status
from datetime import date
from app.shared.security.current_user import get_current_user
from app.slices.partner_loan.period_summary.application.use_case import PeriodSummary
from app.slices.partner_loan.period_summary.infra.repository import PeriodSummaryRepository
from app.slices.partner_loan.period_summary.ui.schemas import LoanPeriodSummaryResponse

router = APIRouter()
use_case = PeriodSummary(PeriodSummaryRepository())


@router.get("/period-summary", response_model=LoanPeriodSummaryResponse)
async def route(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user=Depends(get_current_user),
):
    try:
        return await use_case.execute(start_date=start_date, end_date=end_date)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
