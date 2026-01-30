from fastapi import APIRouter, Depends

from app.shared.security.current_user import get_current_user
from app.slices.products.list_products.ui.schemas import ProductResponse
from app.slices.products.list_products.application.use_case import ListProducts
from app.slices.products.list_products.infra.repository import ListProductsRepository
from typing import List

router = APIRouter()

use_case = ListProducts(ListProductsRepository())

@router.get("/", response_model=List[ProductResponse])
async def route(current_user=Depends(get_current_user)):
    return await use_case.execute()
