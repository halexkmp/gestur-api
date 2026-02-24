from datetime import date, datetime
from decimal import Decimal
from tortoise.functions import Sum
from app.shared.db.models import SalaryAdvance, Employee


async def ensure_monthly_advances_do_not_exceed_salary(
    employee: Employee,
    new_amount: Decimal,
    advance_month: date,
):
    """
    Ensures that the sum of advances for the given employee in the month of
    `advance_month` (based on SalaryAdvance.advance_date) plus `new_amount`
    does not exceed the employee's salary.
    """
    # Normalize to first day of month
    start_of_month = date(year=advance_month.year, month=advance_month.month, day=1)
    # compute the first day of next month
    if start_of_month.month == 12:
        next_month_start = date(year=start_of_month.year + 1, month=1, day=1)
    else:
        next_month_start = date(year=start_of_month.year, month=start_of_month.month + 1, day=1)

    agg = await SalaryAdvance.filter(
        employee=employee,
        advance_date__gte=start_of_month,
        advance_date__lt=next_month_start,
    ).annotate(total=Sum("amount")).values("total")

    current_total = (agg[0]["total"] if agg and agg[0]["total"] is not None else Decimal("0"))

    try:
        additional = Decimal(new_amount)
    except Exception:
        additional = Decimal(str(new_amount))

    salary = employee.salary
    total_with_new = current_total + additional

    if total_with_new > salary:
        raise ValueError("Sum of salary advances for the current month cannot exceed the employee's salary")
