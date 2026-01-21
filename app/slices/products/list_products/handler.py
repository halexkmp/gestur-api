from app.layers.db.models import Product

async def list_products():
    return await Product.all()
