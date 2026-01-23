from fastapi import APIRouter, Depends
from app.shared.security.current_password import get_current_user
from app.slices.products.create_product.application.use_case import CreateProduct
from app.slices.products.create_product.infra.repository import CreateProductRepository
from app.slices.products.create_product.ui.schemas import ProductCreate, ProductResponse

router = APIRouter()

use_case = CreateProduct(CreateProductRepository())

@router.post("/", response_model=ProductResponse, status_code=201)
async def route(data: ProductCreate, current_user=Depends(get_current_user)):
    return await use_case.execute(
        name=data.name,
        type=data.type,
        default_price=data.default_price,
        has_stock=data.has_stock,
        stock_quantity=data.stock_quantity,
        active=data.active,
    )
