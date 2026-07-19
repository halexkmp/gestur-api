from datetime import time
from decimal import Decimal
from app.slices.employees.get_lateness_config.infra.repository import GetLatenessConfigurationRepository

DEFAULT_CONFIG = {
    "enabled": False,
    "expected_entrance_time": time(0, 0, 0),
    "tolerance_minutes": 0,
    "deduction_interval_minutes": 0,
    "deduction_value": Decimal("0"),
}


class GetLatenessConfiguration:
    def __init__(self, repository: GetLatenessConfigurationRepository):
        self.repository = repository

    async def execute(self) -> dict:
        config = await self.repository.get()
        if not config:
            return dict(DEFAULT_CONFIG)

        return {
            "enabled": config.enabled,
            "expected_entrance_time": config.expected_entrance_time,
            "tolerance_minutes": config.tolerance_minutes,
            "deduction_interval_minutes": config.deduction_interval_minutes,
            "deduction_value": Decimal(config.deduction_value),
        }
