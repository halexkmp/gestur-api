from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
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
    passengers_per_unit: int


@dataclass(frozen=True)
class LinkedProduct:
    default_price: Decimal
    passengers_per_unit: int


@dataclass(frozen=True)
class DayFigures:
    passengers_detected: int
    passengers_sold: int
    passengers_below_default_price: int
    passengers_justified: int
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


def count_passengers(lines: list[SoldLine]) -> int:
    """Sold units become passengers: one tandem sold is 2 passengers."""
    return sum(line.quantity * line.passengers_per_unit for line in lines)


def _average_passenger_price(
    sales_amount: Decimal,
    passengers_sold: int,
    linked: list[LinkedProduct],
) -> Decimal:
    if passengers_sold > 0:
        return sales_amount / passengers_sold
    if linked:
        return sum(
            (product.default_price / product.passengers_per_unit for product in linked),
            Decimal("0"),
        ) / len(linked)
    return Decimal("0")


def calculate_day(
    passengers: int,
    lines: list[SoldLine],
    justified: int,
    device_hours: int,
    clock_suspect_trips: int,
    linked: list[LinkedProduct],
) -> DayFigures:
    passengers_sold = count_passengers(lines)
    below_default = count_passengers([line for line in lines if line.unit_price < line.default_price])
    sales_amount = sum((line.total_price for line in lines), Decimal("0"))

    unexplained = max(passengers - passengers_sold - justified, 0)
    sold_above_detected = max(passengers_sold + justified - passengers, 0)

    if unexplained > 0:
        status = TirolesaAuditStatus.UNEXPLAINED
    elif sold_above_detected > 0:
        status = TirolesaAuditStatus.SOLD_ABOVE_DETECTED
    else:
        status = TirolesaAuditStatus.BALANCED

    estimated = unexplained * _average_passenger_price(sales_amount, passengers_sold, linked)

    return DayFigures(
        passengers_detected=passengers,
        passengers_sold=passengers_sold,
        passengers_below_default_price=below_default,
        passengers_justified=justified,
        unexplained=unexplained,
        sold_above_detected=sold_above_detected,
        sales_amount=sales_amount.quantize(CENTS, rounding=ROUND_HALF_UP),
        estimated_unpaid_value=estimated.quantize(CENTS, rounding=ROUND_HALF_UP),
        status=status,
        device_hours=device_hours,
        clock_suspect_trips=clock_suspect_trips,
        sensor_warning=device_hours == 0 or clock_suspect_trips > 0,
    )
