from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List

from app.shared.db.models import TirolesaJustification
from app.slices.tirolesa.get_daily_audit.domain.rules import (
    DayFigures,
    LinkedProduct,
    SoldLine,
    calculate_day,
    day_start_utc,
    local_date,
    trip_audit_date,
)
from app.slices.tirolesa.get_daily_audit.infra.repository import GetDailyAuditRepository

MAX_RANGE_DAYS = 62


@dataclass(frozen=True)
class AuditDay:
    date: date
    figures: DayFigures
    justifications: List[TirolesaJustification]


class GetDailyAudit:
    def __init__(self, repository: GetDailyAuditRepository):
        self.repository = repository

    async def execute(self, date_from: date, date_to: date) -> List[AuditDay]:
        if date_from > date_to:
            raise ValueError("date_from must not be after date_to")
        total_days = (date_to - date_from).days + 1
        if total_days > MAX_RANGE_DAYS:
            raise ValueError(f"Date range must not exceed {MAX_RANGE_DAYS} days")

        offset = await self.repository.get_utc_offset_minutes()
        start = day_start_utc(date_from, offset)
        end = day_start_utc(date_to + timedelta(days=1), offset)

        links = await self.repository.get_linked_products()
        links_by_product = {link.product.id: link for link in links}
        linked = [
            LinkedProduct(link.product.default_price, link.passengers_per_unit)
            for link in links
        ]

        passengers_by_day: dict[date, int] = defaultdict(int)
        suspect_by_day: dict[date, int] = defaultdict(int)
        for trip in await self.repository.get_trips(start, end):
            day = trip_audit_date(trip.start_at, trip.received_at, trip.clock_suspect, offset)
            passengers_by_day[day] += trip.passengers
            if trip.clock_suspect:
                suspect_by_day[day] += 1

        lines_by_day: dict[date, list[SoldLine]] = defaultdict(list)
        items = await self.repository.get_sale_items(list(links_by_product), start, end) if links else []
        for item in items:
            link = links_by_product[item.product_id]
            lines_by_day[local_date(item.sale.created_at, offset)].append(
                SoldLine(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                    default_price=link.product.default_price,
                    passengers_per_unit=link.passengers_per_unit,
                )
            )

        justifications_by_day: dict[date, list[TirolesaJustification]] = defaultdict(list)
        for justification in await self.repository.get_justifications(date_from, date_to):
            justifications_by_day[justification.audit_date].append(justification)

        hours_by_day: dict[date, int] = defaultdict(int)
        for hour in set(await self.repository.get_device_hours(start, end)):
            hours_by_day[local_date(hour, offset)] += 1

        days = []
        for index in range(total_days):
            day = date_from + timedelta(days=index)
            day_justifications = justifications_by_day[day]
            days.append(
                AuditDay(
                    date=day,
                    figures=calculate_day(
                        passengers=passengers_by_day[day],
                        lines=lines_by_day[day],
                        justified=sum(j.quantity for j in day_justifications),
                        device_hours=hours_by_day[day],
                        clock_suspect_trips=suspect_by_day[day],
                        linked=linked,
                    ),
                    justifications=day_justifications,
                )
            )
        return days
