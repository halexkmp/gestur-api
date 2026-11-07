from fastapi import APIRouter, Depends, status

from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import ensure_admin_or_manager
from app.slices.tirolesa.create_justification.application.use_case import CreateJustification
from app.slices.tirolesa.create_justification.infra.repository import CreateJustificationRepository
from .schemas import CreateJustificationRequest, CreateJustificationResponse

router = APIRouter()

use_case = CreateJustification(CreateJustificationRepository())


@router.post(
    "/audit/justifications",
    response_model=CreateJustificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def route(data: CreateJustificationRequest, current_user=Depends(get_current_user)):
    ensure_admin_or_manager(current_user)
    justification = await use_case.execute(
        audit_date=data.audit_date,
        quantity=data.quantity,
        justification_type=data.type,
        reason=data.reason,
        created_by_id=current_user.id,
    )
    return CreateJustificationResponse(
        id=justification.id,
        audit_date=justification.audit_date,
        quantity=justification.quantity,
        type=justification.type,
        reason=justification.reason,
        created_at=justification.created_at,
    )
