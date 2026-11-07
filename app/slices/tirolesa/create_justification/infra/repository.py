from datetime import date
from uuid import UUID

from app.shared.db.enums import TirolesaJustificationType
from app.shared.db.models import TirolesaJustification


class CreateJustificationRepository:
    async def create(
        self,
        audit_date: date,
        quantity: int,
        justification_type: TirolesaJustificationType,
        reason: str,
        created_by_id: UUID,
    ) -> TirolesaJustification:
        return await TirolesaJustification.create(
            audit_date=audit_date,
            quantity=quantity,
            type=justification_type,
            reason=reason,
            created_by_id=created_by_id,
        )
