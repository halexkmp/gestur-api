from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.shared.security.current_user import get_current_user
from app.slices.partner_loan.register_payment.application.use_case import RegisterPayment
from app.slices.partner_loan.register_payment.infra.repository import RegisterPaymentRepository
from app.slices.partner_loan.register_payment.ui.schemas import PaymentRegisterRequest, PaymentResponse

router = APIRouter()
use_case = RegisterPayment(RegisterPaymentRepository())

@router.post("/{installment_id}/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def route(
    installment_id: UUID,
    data: PaymentRegisterRequest,
    current_user=Depends(get_current_user)
):
    try:
        payment, _ = await use_case.execute(
            installment_id=installment_id,
            amount=data.amount,
            payment_date=data.payment_date,
            notes=data.notes,
        )
        return payment
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
