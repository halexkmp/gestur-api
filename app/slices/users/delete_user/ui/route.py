from fastapi import APIRouter, Depends
from uuid import UUID
from app.shared.security.current_password import get_current_user
from app.slices.users.delete_user.application.use_case import DeleteUser
from app.slices.users.delete_user.infra.repository import DeleteUserRepository

router = APIRouter()

use_case = DeleteUser(DeleteUserRepository())

@router.delete("/{user_id}", status_code=204)
async def route(user_id: UUID, current_user=Depends(get_current_user)):
    return await use_case.execute(user_id)
