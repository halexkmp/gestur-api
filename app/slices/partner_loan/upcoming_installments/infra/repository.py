from datetime import date
from typing import Optional
from uuid import UUID
from app.shared.db.enums import LoanInstallmentStatus, LoanStatus
from app.shared.db.models import LoanInstallment


class UpcomingInstallmentsRepository:
    async def list_due_installments(
        self,
        start_date: Optional[date],
        end_date: date,
        partner_id: Optional[UUID] = None,
        limit: Optional[int] = None,
    ) -> list[LoanInstallment]:
        # start_date is None when the caller asked to include overdue
        # installments: no lower bound, reaching back over the whole history.
        queryset = (
            LoanInstallment.filter(due_date__lte=end_date)
            .exclude(loan__status=LoanStatus.CANCELED)
            .exclude(status=LoanInstallmentStatus.PAID)
        )

        if start_date is not None:
            queryset = queryset.filter(due_date__gte=start_date)

        if partner_id is not None:
            queryset = queryset.filter(loan__partner_id=partner_id)

        queryset = queryset.prefetch_related("loan__partner", "payments").order_by(
            "due_date", "loan_id", "installment_number"
        )

        # Truncated in SQL, after ordering: include_overdue has no lower bound,
        # so slicing in Python would load the whole history to return a few rows.
        if limit is not None:
            queryset = queryset.limit(limit)

        return await queryset
