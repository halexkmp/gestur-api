from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from math import ceil
from uuid import UUID

from app.shared.db.enums import TirolesaAuditStatus

CENTS = Decimal("0.01")


@dataclass(frozen=True)
class SoldLine:
    product_id: UUID
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    default_price: Decimal
    units_per_descent: int


@dataclass(frozen=True)
class LinkedProduct:
    default_price: Decimal
    units_per_descent: int


@dataclass(frozen=True)
class DayFigures:
    descents_detected: int
    descents_sold: int
    descents_below_default_price: int
    descents_justified: int
    unexplained: int
    sold_above_detected: int
    sales_amount: Decimal
    estimated_unpaid_value: Decimal
    status: TirolesaAuditStatus
    device_hours: int
    clock_suspect_trips: int
    sensor_warning: bool


def local_date(moment: datetime, utc_offset_minutes: int) -> date:
    return (moment + timedelta(minutes=utc_offset_minutes)).date()


def day_start_utc(day: date, utc_offset_minutes: int) -> datetime:
    return datetime.combine(day, time.min, timezone.utc) - timedelta(minutes=utc_offset_minutes)


def trip_audit_date(
    start_at: datetime,
    received_at: datetime,
    clock_suspect: bool,
    utc_offset_minutes: int,
) -> date:
    return local_date(received_at if clock_suspect else start_at, utc_offset_minutes)


def count_descents(lines: list[SoldLine]) -> int:
    """Sold units per product become whole descents: 3 people in pairs need 2 descents."""
    units: dict[UUID, int] = defaultdict(int)
    units_per_descent: dict[UUID, int] = {}
    for line in lines:
        units[line.product_id] += line.quantity
        units_per_descent[line.product_id] = line.units_per_descent
    return sum(ceil(total / units_per_descent[product_id]) for product_id, total in units.items())


def _average_descent_price(
    sales_amount: Decimal,
    descents_sold: int,
    linked: list[LinkedProduct],
) -> Decimal:
    if descents_sold > 0:
        return sales_amount / descents_sold
    if linked:
        return sum(
            (product.default_price * product.units_per_descent for product in linked),
            Decimal("0"),
        ) / len(linked)
    return Decimal("0")


def calculate_day(
    trips: int,
    lines: list[SoldLine],
    justified: int,
    device_hours: int,
    clock_suspect_trips: int,
    linked: list[LinkedProduct],
) -> DayFigures:
    descents_sold = count_descents(lines)
    below_default = count_descents([line for line in lines if line.unit_price < line.default_price])
    sales_amount = sum((line.total_price for line in lines), Decimal("0"))

    unexplained = max(trips - descents_sold - justified, 0)
    sold_above_detected = max(descents_sold + justified - trips, 0)

    if unexplained > 0:
        status = TirolesaAuditStatus.UNEXPLAINED
    elif sold_above_detected > 0:
        status = TirolesaAuditStatus.SOLD_ABOVE_DETECTED
    else:
        status = TirolesaAuditStatus.BALANCED

    estimated = unexplained * _average_descent_price(sales_amount, descents_sold, linked)

    return DayFigures(
        descents_detected=trips,
        descents_sold=descents_sold,
        descents_below_default_price=below_default,
        descents_justified=justified,
        unexplained=unexplained,
        sold_above_detected=sold_above_detected,
        sales_amount=sales_amount.quantize(CENTS, rounding=ROUND_HALF_UP),
        estimated_unpaid_value=estimated.quantize(CENTS, rounding=ROUND_HALF_UP),
        status=status,
        device_hours=device_hours,
        clock_suspect_trips=clock_suspect_trips,
        sensor_warning=device_hours == 0 or clock_suspect_trips > 0,
    )
