from fastapi import APIRouter, Depends, HTTPException, status

from app.shared.security.current_user import get_current_user
from app.shared.security.permissions import ensure_admin_or_manager
from app.slices.tirolesa.link_product.application.use_case import (
    LinkProduct,
    ProductAlreadyLinked,
    ProductNotFound,
)
from app.slices.tirolesa.link_product.infra.repository import LinkProductRepository
from .schemas import LinkProductRequest, LinkProductResponse

router = APIRouter()

use_case = LinkProduct(LinkProductRepository())


@router.post("/products", response_model=LinkProductResponse, status_code=status.HTTP_201_CREATED)
async def route(data: LinkProductRequest, current_user=Depends(get_current_user)):
    ensure_admin_or_manager(current_user)
    try:
        link = await use_case.execute(
            product_id=data.product_id,
            units_per_descent=data.units_per_descent,
        )
    except ProductNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    except ProductAlreadyLinked:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product already linked")
    return LinkProductResponse(
        id=link.id,
        product_id=data.product_id,
        units_per_descent=link.units_per_descent,
    )
