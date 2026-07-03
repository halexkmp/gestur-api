from decimal import Decimal
from uuid import UUID
from datetime import date
from tortoise.transactions import in_transaction

from app.shared.db.models import Partner, Loan, LoanInstallment
from app.slices.partner_loan.create_loan.infra.repository import CreateLoanRepository
from app.slices.partner_loan.create_loan.domain.rules import (
    check_partner_eligibility,
    generate_due_dates,
    validate_amount_dates,
)

class CreateLoan:
    def __init__(self, repository: CreateLoanRepository):
        self.repository = repository

    async def execute(
        self,
        partner_id: UUID,
        principal_amount: Decimal,
        interest_rate: Decimal,
        total_amount: Decimal,
        installments: int,
        due_day: int,
        start_date: date,
        end_date: date,
    ) -> Loan:
        # 1. Load partner
        partner = await Partner.get_or_none(id=partner_id)
        if not partner:
            raise ValueError("Partner not found")

        # 2. Check partner eligibility
        check_partner_eligibility(partner)

        # 3. Validate amounts and dates
        validate_amount_dates(due_day, end_date, installments, interest_rate,
                              principal_amount, start_date, total_amount)

        # 4. Generate installment due dates
        due_dates = generate_due_dates(start_date, due_day, installments)

        # 5. Initialize Loan
        loan = Loan(
            partner=partner,
            principal_amount=principal_amount,
            interest_rate=interest_rate,
            total_amount=total_amount,
            installments=installments,
            due_day=due_day,
            start_date=start_date,
            end_date=end_date,
        )

        # 6. Save with transaction
        async with in_transaction():
            # Save the loan first
            saved_loan = await self.repository.save_loan(loan)

            # Generate installments
            installment_amount = round(total_amount / Decimal(installments), 2)
            db_installments = []
            for i in range(1, installments + 1):
                db_installments.append(
                    LoanInstallment(
                        loan=saved_loan,
                        installment_number=i,
                        amount=installment_amount,
                        due_date=due_dates[i - 1],
                        paid=False,
                    )
                )
            
            # Save installments bulk
            await self.repository.save_installments(db_installments)

        return saved_loan
