from fastapi import APIRouter, Depends
from app.shared.security.current_password import get_current_user
from .schemas import ProductResponse, ProductUpdate
from app.slices.products.update_product.application.use_case import UpdateProduct
from app.slices.products.update_product.infra.repository import UpdateProductRepository
from uuid import UUID

router = APIRouter()

use_case = UpdateProduct(UpdateProductRepository())

@router.put("/{product_id}", response_model=ProductResponse)
async def route(product_id: UUID, product_in: ProductUpdate, current_user=Depends(get_current_user)):
    return await use_case.execute(
        product_id=product_id,
        name=product_in.name,
        type=product_in.type,
        default_price=product_in.default_price,
        stock_quantity=product_in.stock_quantity,
        active=product_in.active,
    )
