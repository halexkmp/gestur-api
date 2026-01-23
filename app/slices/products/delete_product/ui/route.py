from fastapi import APIRouter, Depends
from app.shared.security.current_password import get_current_user
from app.slices.products.delete_product.application.use_case import DeleteProduct
from app.slices.products.delete_product.infra.repository import DeleteProductRepository
from uuid import UUID

router = APIRouter()

use_case = DeleteProduct(DeleteProductRepository())

@router.delete("/{product_id}", status_code=204)
async def route(product_id: UUID, current_user=Depends(get_current_user)):
    return await use_case.execute(product_id)
