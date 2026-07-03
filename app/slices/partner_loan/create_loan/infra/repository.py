from app.shared.db.models import Loan, LoanInstallment

class CreateLoanRepository:
    async def save_loan(self, loan: Loan) -> Loan:
        await loan.save()
        return loan

    async def save_installments(self, installments: list[LoanInstallment]) -> list[LoanInstallment]:
        await LoanInstallment.bulk_create(installments)
        return installments
