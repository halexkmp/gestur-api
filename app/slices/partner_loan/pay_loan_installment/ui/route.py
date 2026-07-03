from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.partner_loan.pay_loan_installment.application.use_case import PayLoanInstallment
from app.slices.partner_loan.pay_loan_installment.infra.repository import PayLoanInstallmentRepository
from app.slices.partner_loan.pay_loan_installment.ui.schemas import PayInstallmentRequest
from app.slices.partner_loan.create_loan.ui.schemas import LoanInstallmentResponse

router = APIRouter()
use_case = PayLoanInstallment(PayLoanInstallmentRepository())

@router.patch("/{installment_id}/pay", response_model=LoanInstallmentResponse)
async def route(
    installment_id: UUID,
    data: PayInstallmentRequest = None,
    current_user=Depends(get_current_user)
):
    try:
        p_date = data.payment_date if data is not None else None
        return await use_case.execute(installment_id, p_date)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
