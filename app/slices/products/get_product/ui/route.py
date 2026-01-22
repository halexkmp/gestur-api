from fastapi import APIRouter, Depends
from app.layers.auth import get_current_user
from app.slices.products.ui.schemas import ProductResponse
from app.slices.products.get_product.application.handler import get_product
from uuid import UUID

router = APIRouter()

@router.get("/{product_id}", response_model=ProductResponse)
async def route(product_id: UUID, current_user = Depends(get_current_user)):
    return await get_product(product_id)
