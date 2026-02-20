from datetime import datetime
from decimal import Decimal
from tortoise.functions import Sum
from app.shared.db.models import SalaryAdvance, Employee


async def ensure_monthly_advances_do_not_exceed_salary(employee: Employee, new_amount: Decimal):
    """
    Ensures the sum of advances for the current month (including the new_amount)
    does not exceed the employee's salary. Raises ValueError if it would exceed.
    """
    if employee is None:
        raise ValueError("Employee not found")

    # Calculate current month date range [start, next_month_start)
    now = datetime.now()
    start_of_month = datetime(year=now.year, month=now.month, day=1)
    # compute the first day of next month
    if now.month == 12:
        next_month_start = datetime(year=now.year + 1, month=1, day=1)
    else:
        next_month_start = datetime(year=now.year, month=now.month + 1, day=1)

    agg = await SalaryAdvance.filter(
        employee=employee,
        created_at__gte=start_of_month,
        created_at__lt=next_month_start,
    ).annotate(total=Sum("amount")).values("total")

    current_total = agg[0]["total"] or Decimal("0")

    try:
        additional = Decimal(new_amount)
    except Exception:
        additional = Decimal(str(new_amount))

    # Ensure both sides are Decimal
    salary = employee.salary
    total_with_new = current_total + additional

    if total_with_new > salary:
        raise ValueError("Sum of salary advances for the current month cannot exceed the employee's salary")
