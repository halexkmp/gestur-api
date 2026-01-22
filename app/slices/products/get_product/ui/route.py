from fastapi import APIRouter, Depends
from app.shared.auth import get_current_user
from .schemas import ProductResponse
from app.slices.products.get_product.application.use_case import GetProduct
from app.slices.products.get_product.infra.repository import GetProductRepository
from uuid import UUID

router = APIRouter()

use_case = GetProduct(GetProductRepository())

@router.get("/{product_id}", response_model=ProductResponse)
async def route(product_id: UUID, current_user = Depends(get_current_user)):
    return await use_case.execute(product_id)
