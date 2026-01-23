from fastapi import APIRouter, Depends
from .schemas import ProductResponse
from app.slices.products.get_product.application.use_case import GetProduct
from app.slices.products.get_product.infra.repository import GetProductRepository
from uuid import UUID

router = APIRouter()

use_case = GetProduct(GetProductRepository())

@router.get("/{product_id}", response_model=ProductResponse)
async def route(product_id: UUID):
    return await use_case.execute(product_id)
