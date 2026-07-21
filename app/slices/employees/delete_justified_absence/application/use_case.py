from uuid import UUID
from app.slices.employees.delete_justified_absence.infra.repository import DeleteJustifiedAbsenceRepository

class DeleteJustifiedAbsence:
    def __init__(self, repository: DeleteJustifiedAbsenceRepository):
        self.repository = repository

    async def execute(self, absence_id: UUID) -> bool:
        return await self.repository.delete(absence_id)
