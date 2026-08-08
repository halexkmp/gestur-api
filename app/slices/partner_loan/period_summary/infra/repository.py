from datetime import date
from app.shared.db.enums import LoanStatus
from app.shared.db.models import LoanInstallment


class PeriodSummaryRepository:
    async def list_installments_in_range(
        self, start_date: date, end_date: date
    ) -> list[LoanInstallment]:
        return await (
            LoanInstallment.filter(due_date__gte=start_date, due_date__lte=end_date)
            .exclude(loan__status=LoanStatus.CANCELED)
            .prefetch_related("loan__partner", "payments")
            .order_by("due_date", "installment_number")
        )
