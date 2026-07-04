from fastapi import APIRouter, Depends
from typing import List
from app.shared.security.current_user import get_current_user
from app.slices.partner_loan.list_loans.application.use_case import ListLoans
from app.slices.partner_loan.list_loans.infra.repository import ListLoansRepository
from app.slices.partner_loan.list_loans.ui.schemas import LoanResponse

router = APIRouter()
use_case = ListLoans(ListLoansRepository())

@router.get("/", response_model=List[LoanResponse])
async def route(partner_id: str, current_user=Depends(get_current_user)):
    return await use_case.execute(partner_id)
