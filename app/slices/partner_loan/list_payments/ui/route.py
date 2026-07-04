from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List
from app.shared.security.current_user import get_current_user
from app.slices.partner_loan.list_payments.application.use_case import ListPayments
from app.slices.partner_loan.list_payments.infra.repository import ListPaymentsRepository
from app.slices.partner_loan.list_payments.ui.schemas import PaymentResponse

router = APIRouter()
use_case = ListPayments(ListPaymentsRepository())

@router.get("/{installment_id}/payments", response_model=List[PaymentResponse])
async def route(
    installment_id: UUID,
    current_user=Depends(get_current_user)
):
    try:
        return await use_case.execute(installment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
