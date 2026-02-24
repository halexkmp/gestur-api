from typing import Sequence
from app.shared.db.models import SalaryAdvance, Employee


class CreateSalaryAdvanceRepository:
    async def save_many(
        self,
        advances: Sequence[SalaryAdvance],
    ):
        return await SalaryAdvance.bulk_create(list(advances))
