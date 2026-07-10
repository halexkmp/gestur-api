from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.partner_loan.get_loan_summary.application.use_case import GetLoanSummary
from app.slices.partner_loan.get_loan_summary.infra.repository import GetLoanSummaryRepository
from app.slices.partner_loan.get_loan_summary.ui.schemas import LoanSummaryResponse

router = APIRouter()
use_case = GetLoanSummary(GetLoanSummaryRepository())

@router.get("/{loan_id}/summary", response_model=LoanSummaryResponse)
async def get_loan_summary_route(loan_id: UUID, current_user=Depends(get_current_user)):
    try:
        return await use_case.execute(loan_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
