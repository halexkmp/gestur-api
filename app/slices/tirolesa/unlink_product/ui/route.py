from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import ensure_admin_or_manager
from app.slices.tirolesa.unlink_product.application.use_case import UnlinkProduct
from app.slices.tirolesa.unlink_product.infra.repository import UnlinkProductRepository

router = APIRouter()

use_case = UnlinkProduct(UnlinkProductRepository())


@router.delete("/products/{tirolesa_product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route(tirolesa_product_id: UUID, current_user=Depends(get_current_user)):
    ensure_admin_or_manager(current_user)
    if not await use_case.execute(tirolesa_product_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tirolesa product not found")
    return None
