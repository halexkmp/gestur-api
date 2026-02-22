from uuid import UUID
from app.shared.db.models import SalaryAdvance

class DeleteSalaryAdvanceRepository:
    async def delete(self, advance_id: UUID) -> bool:
        advance = await SalaryAdvance.get_or_none(id=advance_id)
        if not advance:
            return False
        await advance.delete()
        return True
