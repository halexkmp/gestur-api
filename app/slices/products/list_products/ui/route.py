from fastapi import APIRouter
from app.slices.products.list_products.ui.schemas import ProductResponse
from app.slices.products.list_products.application.use_case import ListProducts
from app.slices.products.list_products.infra.repository import ListProductsRepository
from typing import List

router = APIRouter()

use_case = ListProducts(ListProductsRepository())

@router.get("/", response_model=List[ProductResponse])
async def route():
    return await use_case.execute()
