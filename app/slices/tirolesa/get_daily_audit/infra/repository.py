from datetime import date, datetime
from typing import List
from uuid import UUID

from tortoise.expressions import Q

from app.shared.db.enums import SaleStatus
from app.shared.db.models import (
    LatenessConfiguration,
    SaleItem,
    TirolesaDeviceHour,
    TirolesaJustification,
    TirolesaProduct,
    TirolesaTrip,
)


class GetDailyAuditRepository:
    async def get_utc_offset_minutes(self) -> int:
        config = await LatenessConfiguration.all().order_by("created_at").first()
        return config.utc_offset_minutes if config else -180

    async def get_linked_products(self) -> List[TirolesaProduct]:
        return await TirolesaProduct.all().prefetch_related("product")

    async def get_trips(self, start: datetime, end: datetime) -> List[TirolesaTrip]:
        return await TirolesaTrip.filter(
            Q(clock_suspect=False, start_at__gte=start, start_at__lt=end)
            | Q(clock_suspect=True, received_at__gte=start, received_at__lt=end)
        )

    async def get_sale_items(
        self,
        product_ids: List[UUID],
        start: datetime,
        end: datetime,
    ) -> List[SaleItem]:
        return await SaleItem.filter(
            product_id__in=product_ids,
            sale__created_at__gte=start,
            sale__created_at__lt=end,
            sale__status__not=SaleStatus.CANCELED,
        ).prefetch_related("sale")

    async def get_justifications(self, date_from: date, date_to: date) -> List[TirolesaJustification]:
        return await TirolesaJustification.filter(
            is_deleted=False,
            audit_date__gte=date_from,
            audit_date__lte=date_to,
        ).prefetch_related("created_by").order_by("created_at")

    async def get_device_hours(self, start: datetime, end: datetime) -> List[datetime]:
        return await TirolesaDeviceHour.filter(hour__gte=start, hour__lt=end).values_list("hour", flat=True)
