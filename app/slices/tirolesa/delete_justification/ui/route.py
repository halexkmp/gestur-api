from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import ensure_admin_or_manager
from app.slices.tirolesa.delete_justification.application.use_case import DeleteJustification
from app.slices.tirolesa.delete_justification.infra.repository import DeleteJustificationRepository

router = APIRouter()

use_case = DeleteJustification(DeleteJustificationRepository())


@router.delete("/audit/justifications/{justification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route(justification_id: UUID, current_user=Depends(get_current_user)):
    ensure_admin_or_manager(current_user)
    deleted = await use_case.execute(justification_id=justification_id, deleted_by_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Justification not found")
    return None
