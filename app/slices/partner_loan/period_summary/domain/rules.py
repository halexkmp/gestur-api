from datetime import date
from decimal import Decimal


def validate_date_range(start_date: date, end_date: date) -> None:
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date")


def installment_profit_share(
    amount: Decimal, principal_amount: Decimal, total_amount: Decimal
) -> Decimal:
    """Interest portion of a single installment, at full precision.

    Returned unrounded on purpose: the caller sums these and quantizes once,
    so the capital/profit split stays exact against the expected revenue.
    """
    if total_amount == 0:
        return Decimal("0.00")
    return amount * (total_amount - principal_amount) / total_amount


def received_for_installment(
    payment_amounts: list[Decimal], installment_amount: Decimal
) -> Decimal:
    """How much of a single installment counts as received.

    Capped at the installment amount so an overpayment can never push the
    outstanding balance negative.
    """
    return min(sum(payment_amounts, Decimal("0.00")), installment_amount)
