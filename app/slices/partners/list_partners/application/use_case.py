from typing import List
from app.shared.db.models import Partner
from app.slices.partners.list_partners.infra.repository import ListPartnersRepository

class ListPartners:
    def __init__(self, repository: ListPartnersRepository):
        self.repository = repository

    async def execute(self) -> List[Partner]:
        return await self.repository.list()
