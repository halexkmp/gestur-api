from typing import List

from app.shared.db.models import TirolesaProduct
from app.slices.tirolesa.list_products.infra.repository import ListProductsRepository


class ListProducts:
    def __init__(self, repository: ListProductsRepository):
        self.repository = repository

    async def execute(self) -> List[TirolesaProduct]:
        return await self.repository.list()
