from datetime import date
from uuid import UUID

from app.shared.db.enums import TirolesaJustificationType
from app.shared.db.models import TirolesaJustification
from app.slices.tirolesa.create_justification.infra.repository import CreateJustificationRepository


class CreateJustification:
    def __init__(self, repository: CreateJustificationRepository):
        self.repository = repository

    async def execute(
        self,
        audit_date: date,
        quantity: int,
        justification_type: TirolesaJustificationType,
        reason: str,
        created_by_id: UUID,
    ) -> TirolesaJustification:
        return await self.repository.create(
            audit_date=audit_date,
            quantity=quantity,
            justification_type=justification_type,
            reason=reason,
            created_by_id=created_by_id,
        )
