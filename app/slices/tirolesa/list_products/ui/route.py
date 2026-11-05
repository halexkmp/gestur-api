from typing import List

from fastapi import APIRouter, Depends

from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import ensure_admin_or_manager
from app.slices.tirolesa.list_products.application.use_case import ListProducts
from app.slices.tirolesa.list_products.infra.repository import ListProductsRepository
from .schemas import TirolesaProductResponse

router = APIRouter()

use_case = ListProducts(ListProductsRepository())


@router.get("/products", response_model=List[TirolesaProductResponse])
async def route(current_user=Depends(get_current_user)):
    ensure_admin_or_manager(current_user)
    links = await use_case.execute()
    return [
        TirolesaProductResponse(
            id=link.id,
            product_id=link.product.id,
            product_name=link.product.name,
            units_per_descent=link.units_per_descent,
        )
        for link in links
    ]
