from fastapi import APIRouter
from app.slices.partner_loan.create_loan.ui.route import router as create_loan_router
from app.slices.partner_loan.get_loan.ui.route import router as get_loan_router
from app.slices.partner_loan.list_loans.ui.route import router as list_loans_router
from app.slices.partner_loan.update_loan.ui.route import router as update_loan_router
from app.slices.partner_loan.list_loan_installments.ui.route import router as list_installments_router
from app.slices.partner_loan.pay_loan_installment.ui.route import router as pay_installment_router

router = APIRouter()

loans_router = APIRouter(prefix="/loans", tags=["loans"])
loans_router.include_router(create_loan_router)
loans_router.include_router(get_loan_router)
loans_router.include_router(list_loans_router)
loans_router.include_router(update_loan_router)
loans_router.include_router(list_installments_router)

installments_router = APIRouter(prefix="/loan-installments", tags=["loan-installments"])
installments_router.include_router(pay_installment_router)

router.include_router(loans_router)
router.include_router(installments_router)
