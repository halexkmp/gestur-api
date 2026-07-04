from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List
from app.shared.security.current_user import get_current_user
from app.slices.partner_loan.list_loan_installments.application.use_case import ListLoanInstallments
from app.slices.partner_loan.list_loan_installments.infra.repository import ListLoanInstallmentsRepository
from app.slices.partner_loan.list_loan_installments.ui.schemas import LoanInstallmentResponse

router = APIRouter()
use_case = ListLoanInstallments(ListLoanInstallmentsRepository())

@router.get("/{loan_id}/installments", response_model=List[LoanInstallmentResponse])
async def route(loan_id: UUID, current_user=Depends(get_current_user)):
    try:
        return await use_case.execute(loan_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
