from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.partner_loan.get_loan.application.use_case import GetLoan
from app.slices.partner_loan.get_loan.infra.repository import GetLoanRepository
from app.slices.partner_loan.get_loan.ui.schemas import LoanResponse

router = APIRouter()
use_case = GetLoan(GetLoanRepository())

@router.get("/{loan_id}", response_model=LoanResponse)
async def route(loan_id: UUID, current_user=Depends(get_current_user)):
    try:
        return await use_case.execute(loan_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
