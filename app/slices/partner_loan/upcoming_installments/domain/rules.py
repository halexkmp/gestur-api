from datetime import date
from decimal import Decimal
from typing import Optional


def validate_date_range(start_date: date, end_date: date) -> None:
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date")


def resolve_lower_bound(start_date: date, include_overdue: bool) -> Optional[date]:
    """The earliest due date to select, or None for no lower bound at all.

    `include_overdue` reaches back over the entire loan history — there is no
    cutoff. Resolving it here keeps the flag out of the repository, which only
    ever sees an already-decided bound.
    """
    return None if include_overdue else start_date


def received_for_installment(
    payment_amounts: list[Decimal], installment_amount: Decimal
) -> Decimal:
    """How much of a single installment counts as received.

    Capped at the installment amount so an overpayment can never push the
    remaining balance negative.
    """
    return min(sum(payment_amounts, Decimal("0.00")), installment_amount)


def is_overdue_on(due_date: date, reference_date: date) -> bool:
    """Whether an unsettled installment is late as of `reference_date`.

    Named `_on` rather than `is_overdue`: the DTO and the response schema both
    carry a field of that name, and binding it as a local in the use case would
    shadow this function for the whole scope.
    """
    return due_date < reference_date
