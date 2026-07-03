from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.security.current_user import get_current_user
from app.slices.partner_loan.create_loan.application.use_case import CreateLoan
from app.slices.partner_loan.create_loan.infra.repository import CreateLoanRepository
from app.slices.partner_loan.create_loan.ui.schemas import LoanCreateRequest, LoanResponse

router = APIRouter()

use_case = CreateLoan(CreateLoanRepository())

@router.post("/", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def route(data: LoanCreateRequest, current_user=Depends(get_current_user)):
    try:
        loan = await use_case.execute(
            partner_id=data.partner_id,
            principal_amount=data.principal_amount,
            interest_rate=data.interest_rate,
            installments_qty=data.installments_qty,
            due_day=data.due_day,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        return loan
    except ValueError as e:
        err_msg = str(e)
        if "Partner not found" in err_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
