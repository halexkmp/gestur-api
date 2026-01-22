from fastapi import HTTPException
from uuid import UUID
from app.shared.db.models import Product

async def get_product(product_id: UUID):
    product = await Product.get_or_none(id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
