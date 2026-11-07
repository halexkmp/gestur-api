from datetime import datetime
from typing import Optional
from uuid import UUID

from app.shared.db.models import TirolesaJustification


class DeleteJustificationRepository:
    async def get_active(self, justification_id: UUID) -> Optional[TirolesaJustification]:
        return await TirolesaJustification.get_or_none(id=justification_id, is_deleted=False)

    async def soft_delete(
        self,
        justification: TirolesaJustification,
        deleted_by_id: UUID,
        deleted_at: datetime,
    ) -> None:
        justification.is_deleted = True
        justification.deleted_by_id = deleted_by_id
        justification.deleted_at = deleted_at
        await justification.save(update_fields=["is_deleted", "deleted_by_id", "deleted_at"])
