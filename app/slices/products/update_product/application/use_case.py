from uuid import UUID
from fastapi import HTTPException
from app.shared.db.models import Product
from app.slices.products.update_product.ui.schemas import ProductUpdate

async def update_product(product_id: UUID, data: ProductUpdate):
    product = await Product.get_or_none(id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    update_data = data.model_dump(exclude_unset=True)
    await product.update_from_dict(update_data).save()
    return product
