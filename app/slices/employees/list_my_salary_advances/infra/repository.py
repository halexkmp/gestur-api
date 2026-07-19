from typing import List, Optional
from uuid import UUID
from datetime import date

from app.shared.db.models import SalaryAdvance


class ListMyAdvancesRepository:
    async def list(
        self,
        employee_id: UUID,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ) -> List[SalaryAdvance]:
        qs = SalaryAdvance.filter(employee_id=employee_id)
        if month is not None and year is not None:
            start = date(year, month, 1)
            if month == 12:
                next_month_first = date(year + 1, 1, 1)
            else:
                next_month_first = date(year, month + 1, 1)
            qs = qs.filter(advance_date__gte=start, advance_date__lt=next_month_first)
        elif year is not None:
            start = date(year, 1, 1)
            next_year_first = date(year + 1, 1, 1)
            qs = qs.filter(advance_date__gte=start, advance_date__lt=next_year_first)
        qs = qs.order_by("-created_at", "-id")
        return await qs
