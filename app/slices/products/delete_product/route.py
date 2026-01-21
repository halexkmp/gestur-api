from fastapi import APIRouter, Depends
from app.layers.auth import get_current_user
from app.slices.products.delete_product.handler import delete_product
from uuid import UUID

router = APIRouter()

@router.delete("/{product_id}", status_code=204)
async def route(product_id: UUID, current_user = Depends(get_current_user)):
    return await delete_product(product_id)
