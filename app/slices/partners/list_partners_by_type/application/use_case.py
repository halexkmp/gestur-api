from typing import List
from app.shared.db.models import Partner
from app.shared.db.enums import PartnerType
from app.slices.partners.list_partners_by_type.infra.repository import ListPartnersByTypeRepository


class ListPartnersByType:
    def __init__(self, repository: ListPartnersByTypeRepository):
        self.repository = repository

    async def execute(self, type: PartnerType) -> List[Partner]:
        return await self.repository.list_by_type(type=type)
