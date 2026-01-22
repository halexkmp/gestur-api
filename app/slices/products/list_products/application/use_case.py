from app.shared.db.models import Product

async def list_products():
    return await Product.all()
