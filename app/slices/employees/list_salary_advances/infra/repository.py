from typing import List, Optional
from uuid import UUID
from app.shared.db.models import SalaryAdvance


class ListSalaryAdvancesRepository:
    async def list(
        self,
        employee_id: Optional[UUID] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ) -> List[SalaryAdvance]:
        qs = SalaryAdvance.all()
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        if month is not None:
            qs = qs.filter(paid_at__month=month)
        if year is not None:
            qs = qs.filter(paid_at__year=year)
        qs = qs.order_by("-paid_at", "-id")
        return await qs
