from typing import List, Optional
from app.shared.db.models import SalaryAdvance


class ListSalaryAdvancesRepository:
    async def list(
        self,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ) -> List[SalaryAdvance]:
        qs = SalaryAdvance.all()
        if month is not None:
            qs = qs.filter(created_at__month=month)
        if year is not None:
            qs = qs.filter(created__year=year)
        qs = qs.order_by("-created_at", "-id")
        return await qs
