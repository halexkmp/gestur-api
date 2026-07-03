from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.partner_loan.update_loan.application.use_case import UpdateLoan
from app.slices.partner_loan.update_loan.infra.repository import UpdateLoanRepository
from app.slices.partner_loan.update_loan.ui.schemas import LoanUpdateRequest
from app.slices.partner_loan.create_loan.ui.schemas import LoanResponse

router = APIRouter()
use_case = UpdateLoan(UpdateLoanRepository())

@router.put("/{loan_id}", response_model=LoanResponse)
async def route(loan_id: UUID, data: LoanUpdateRequest, current_user=Depends(get_current_user)):
    try:
        return await use_case.execute(
            loan_id=loan_id,
            principal_amount=data.principal_amount,
            interest_rate=data.interest_rate,
            total_amount=data.total_amount,
            installments=data.installments,
            due_day=data.due_day,
            start_date=data.start_date,
            end_date=data.end_date,
            status=data.status,
        )
    except ValueError as e:
        err_msg = str(e)
        if "Loan not found" in err_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
