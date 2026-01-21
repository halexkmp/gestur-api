from fastapi import APIRouter, Depends
from app.layers.auth import get_current_user
from app.slices.products.ui.schemas import ProductResponse, ProductUpdate
from app.slices.products.update_product.handler import update_product
from uuid import UUID

router = APIRouter()

@router.put("/{product_id}", response_model=ProductResponse)
async def route(product_id: UUID, product_in: ProductUpdate, current_user = Depends(get_current_user)):
    return await update_product(product_id, product_in)
