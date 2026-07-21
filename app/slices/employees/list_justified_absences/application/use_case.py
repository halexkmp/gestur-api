from typing import List, Optional
from uuid import UUID

from app.shared.db.models import JustifiedAbsence
from app.slices.employees.list_justified_absences.infra.repository import ListJustifiedAbsencesRepository


class ListJustifiedAbsences:
    def __init__(self, repository: ListJustifiedAbsencesRepository):
        self.repository = repository

    async def execute(
        self,
        employee_id: Optional[UUID] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ) -> List[JustifiedAbsence]:
        return await self.repository.list(employee_id=employee_id, month=month, year=year)
