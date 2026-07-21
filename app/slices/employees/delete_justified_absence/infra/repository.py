from uuid import UUID
from app.shared.db.models import JustifiedAbsence

class DeleteJustifiedAbsenceRepository:
    async def delete(self, absence_id: UUID) -> bool:
        absence = await JustifiedAbsence.get_or_none(id=absence_id)
        if not absence:
            return False
        await absence.delete()
        return True
