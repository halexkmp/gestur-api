from datetime import datetime, timezone
from uuid import UUID

from app.slices.tirolesa.delete_justification.infra.repository import DeleteJustificationRepository


class DeleteJustification:
    def __init__(self, repository: DeleteJustificationRepository):
        self.repository = repository

    async def execute(self, justification_id: UUID, deleted_by_id: UUID) -> bool:
        justification = await self.repository.get_active(justification_id)
        if justification is None:
            return False
        await self.repository.soft_delete(justification, deleted_by_id, datetime.now(timezone.utc))
        return True
