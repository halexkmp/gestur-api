import calendar
from datetime import date
from decimal import Decimal
from app.shared.db.enums import PartnerType
from app.shared.db.models import Partner

def calculate_total_amount(principal_amount: Decimal, interest_rate: Decimal) -> Decimal:
    return round(principal_amount * (Decimal('1') + interest_rate / Decimal('100')), 2)

def check_partner_eligibility(partner: Partner):
    if partner.type != PartnerType.BUGGYMAN:
        raise ValueError("Only partners of type BUGGYMAN are eligible for loans")

def get_due_date_for_month(year: int, month: int, due_day: int) -> date:
    _, last_day = calendar.monthrange(year, month)
    target_day = min(due_day, last_day)
    return date(year, month, target_day)

def generate_due_dates(start_date: date, due_day: int, num_installments: int) -> list[date]:
    due_dates = []
    for i in range(1, num_installments + 1):
        total_months = start_date.month - 1 + i
        target_year = start_date.year + total_months // 12
        target_month = total_months % 12 + 1
        
        due_dates.append(get_due_date_for_month(target_year, target_month, due_day))
    return due_dates

def validate_amount_dates(due_day, end_date, installments, interest_rate, principal_amount, start_date,
                          total_amount):
    if principal_amount <= 0:
        raise ValueError("Principal amount must be greater than zero")
    if interest_rate < 0:
        raise ValueError("Interest rate cannot be negative")
    if total_amount <= 0:
        raise ValueError("Total amount must be greater than zero")
    if installments <= 0:
        raise ValueError("Installments must be greater than zero")
    if due_day < 1 or due_day > 28:
        raise ValueError("Due day must be between 1 and 28")
    if end_date < start_date:
        raise ValueError("End date cannot be before start date")