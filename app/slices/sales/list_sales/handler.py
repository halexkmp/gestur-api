from app.layers.db.models import Sale

async def list_sales():
    return await Sale.all().prefetch_related("items", "payments")
