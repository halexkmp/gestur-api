from app.layers.db.models import Product
from app.slices.products.ui.schemas import ProductCreate

async def create_product(data: ProductCreate):
    return await Product.create(**data.model_dump())
