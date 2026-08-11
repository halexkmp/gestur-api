from fastapi import APIRouter
from app.slices.partner_loan.create_loan.ui.route import router as create_loan_router
from app.slices.partner_loan.get_loan.ui.route import router as get_loan_router
from app.slices.partner_loan.list_loans.ui.route import router as list_loans_router
from app.slices.partner_loan.update_loan.ui.route import router as update_loan_router
from app.slices.partner_loan.get_loan_summary.ui.route import router as get_loan_summary_router
from app.slices.partner_loan.list_loan_installments.ui.route import router as list_installments_router
from app.slices.partner_loan.pay_loan_installment.ui.route import router as pay_installment_router
from app.slices.partner_loan.register_payment.ui.route import router as register_payment_router
from app.slices.partner_loan.list_payments.ui.route import router as list_payments_router
from app.slices.partner_loan.period_summary.ui.route import router as period_summary_router
from app.slices.partner_loan.upcoming_installments.ui.route import router as upcoming_installments_router

router = APIRouter()

loans_router = APIRouter(prefix="/loans", tags=["loans"])
loans_router.include_router(create_loan_router)
# Must precede get_loan_router: GET /{loan_id} would otherwise match the
# literal "period-summary" and "upcoming-installments" segments and fail UUID
# validation with a 422.
loans_router.include_router(period_summary_router)
loans_router.include_router(upcoming_installments_router)
loans_router.include_router(get_loan_router)
loans_router.include_router(get_loan_summary_router)
loans_router.include_router(list_loans_router)
loans_router.include_router(update_loan_router)
loans_router.include_router(list_installments_router)

installments_router = APIRouter(prefix="/loan-installments", tags=["loan-installments"])
installments_router.include_router(pay_installment_router)
installments_router.include_router(register_payment_router)
installments_router.include_router(list_payments_router)

router.include_router(loans_router)
router.include_router(installments_router)
