from datetime import time, timezone
from decimal import Decimal
from app.shared.db.models import LatenessConfiguration


class UpdateLatenessConfigurationRepository:
    async def upsert(
        self,
        enabled: bool,
        expected_entrance_time: time,
        tolerance_minutes: int,
        deduction_interval_minutes: int,
        deduction_value: Decimal,
    ) -> LatenessConfiguration:
        # Column is TIMETZ (matching the migration-seeded CURRENT_TIME row); a
        # naive `time` from request parsing must carry tzinfo before it can be
        # bound to that column.
        if expected_entrance_time.tzinfo is None:
            expected_entrance_time = expected_entrance_time.replace(tzinfo=timezone.utc)

        config = await LatenessConfiguration.all().order_by("created_at").first()
        if not config:
            return await LatenessConfiguration.create(
                enabled=enabled,
                expected_entrance_time=expected_entrance_time,
                tolerance_minutes=tolerance_minutes,
                deduction_interval_minutes=deduction_interval_minutes,
                deduction_value=deduction_value,
            )

        config.enabled = enabled
        config.expected_entrance_time = expected_entrance_time
        config.tolerance_minutes = tolerance_minutes
        config.deduction_interval_minutes = deduction_interval_minutes
        config.deduction_value = deduction_value
        await config.save()
        return config
