"""Populate the database with synthetic employee-domain data for load testing.

Creates 100 users (role EMPLOYEE) each linked to one employee, plus the
supporting records needed to exercise the employees/journey use cases under
load: schedules, salary advances, a lateness configuration, justified
absences, and journey registries (check-in/check-out) for the next 30 days
with a mix of on-time and late entrances so "discount by lateness" has real
data to compute against.

Idempotent: employees are tagged with usernames "load_employee_001".."load_employee_100";
re-running skips any that already exist instead of duplicating them.

Requires the DB schema to already be migrated (`aerich upgrade`, or a dev run
with GENERATE_SCHEMAS=true) and DATABASE_URL configured via .env.

Usage:
    uv run python scripts/seed_load_test_data.py
"""

import asyncio
import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import uuid4

from tortoise import Tortoise
from tortoise.transactions import in_transaction

from app.config import TORTOISE_ORM
from app.shared.db.enums import UserRole
from app.shared.db.models import (
    Employee,
    EmployeeSchedule,
    JourneyRegistry,
    JustifiedAbsence,
    LatenessConfiguration,
    Role,
    SalaryAdvance,
    User,
)
from app.slices.users.create_user.infra.password_hash_create import PasswordHashCreate

EMPLOYEE_COUNT = 100
JOURNEY_DAYS_AHEAD = 30
DEFAULT_PASSWORD = "Password123!"
USERNAME_PREFIX = "load_employee_"

FIRST_NAMES = [
    "Ana", "Bruno", "Carla", "Daniel", "Eduarda", "Felipe", "Gabriela", "Hugo",
    "Isabela", "Joao", "Karina", "Lucas", "Mariana", "Nicolas", "Olivia",
    "Pedro", "Queila", "Rafael", "Sabrina", "Thiago", "Ursula", "Vitor",
    "Wesley", "Ximena", "Yasmin", "Zeca", "Camila", "Diego", "Elaine", "Fabio",
]
LAST_NAMES = [
    "Silva", "Souza", "Costa", "Pereira", "Oliveira", "Santos", "Rodrigues",
    "Almeida", "Nascimento", "Lima", "Araujo", "Fernandes", "Carvalho",
    "Gomes", "Martins", "Rocha", "Ribeiro", "Alves", "Monteiro", "Cardoso",
]

BASE_LATITUDE = -3.7327
BASE_LONGITUDE = -38.5267

# UTC-3 local time, 08:00 expected entrance, 10-minute tolerance, R$10 per
# 15-minute late block — deliberately generous so seeded journeys produce
# visible late-day/deduction totals in get_salary_summary.
LATENESS_CONFIG_DEFAULTS = dict(
    enabled=True,
    expected_entrance_time=time(8, 0),
    tolerance_minutes=10,
    deduction_interval_minutes=15,
    deduction_value=Decimal("10.00"),
    utc_offset_minutes=-180,
)


async def seed_roles() -> dict[UserRole, Role]:
    roles: dict[UserRole, Role] = {}
    for role in UserRole:
        role_obj, _ = await Role.get_or_create(name=role)
        roles[role] = role_obj
    return roles


async def seed_lateness_configuration() -> LatenessConfiguration:
    existing = await LatenessConfiguration.all().order_by("created_at").first()
    if existing:
        return existing
    return await LatenessConfiguration.create(**LATENESS_CONFIG_DEFAULTS)


def random_name() -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_pix_key() -> str:
    return f"pix-{uuid4().hex[:16]}"


def random_salary() -> Decimal:
    cents = random.randrange(140000, 800000, 100)  # R$1400.00 - R$8000.00
    return Decimal(cents) / Decimal(100)


def build_schedule_flags() -> dict[str, bool]:
    weekday_fields = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    weekend_fields = ["saturday", "sunday"]
    flags = {field: random.random() < 0.9 for field in weekday_fields}
    flags.update({field: random.random() < 0.2 for field in weekend_fields})
    if not any(flags.values()):
        flags["monday"] = True
    return flags


def entrance_offset_minutes(config: LatenessConfiguration) -> int:
    """Minutes relative to expected_entrance_time; ~35% chance of being late."""
    if random.random() < 0.35:
        return random.randint(config.tolerance_minutes + 5, config.tolerance_minutes + 90)
    return random.randint(-15, config.tolerance_minutes)


def to_utc(day: date, local_time_of_day: time, utc_offset_minutes: int) -> datetime:
    local_dt = datetime.combine(day, local_time_of_day)
    return local_dt - timedelta(minutes=utc_offset_minutes)


async def seed_employee(
    index: int,
    employee_role: Role,
    lateness_config: LatenessConfiguration,
    password_hasher: PasswordHashCreate,
) -> list[JourneyRegistry]:
    username = f"{USERNAME_PREFIX}{index:03d}"
    if await User.exists(username=username):
        return []

    name = random_name()
    user = await User.create(
        name=name,
        username=username,
        password_hash=password_hasher.get_password_hash(DEFAULT_PASSWORD),
        active=True,
    )
    await user.roles.add(employee_role)

    start_date = date.today() - timedelta(days=random.randint(30, 900))
    employee = await Employee.create(
        name=name,
        pix_key=random_pix_key(),
        salary=random_salary(),
        start_date=start_date,
        active=True,
        user=user,
    )

    await EmployeeSchedule.create(employee=employee, **build_schedule_flags())

    advance_day = min(date.today().day, 20)
    advance_amount = (employee.salary * Decimal(random.choice(["0.10", "0.15", "0.20"]))).quantize(Decimal("0.01"))
    await SalaryAdvance.create(
        employee=employee,
        amount=advance_amount,
        advance_date=date.today().replace(day=advance_day),
        note="Adiantamento salarial (seed - load test)",
    )

    if random.random() < 0.15:
        absence_offset = random.randint(1, 10)
        absence_date = date.today() - timedelta(days=absence_offset)
        await JustifiedAbsence.create(
            employee=employee,
            absence_date=absence_date,
            reason="Atestado medico (seed - load test)",
        )

    journeys: list[JourneyRegistry] = []
    for day_offset in range(JOURNEY_DAYS_AHEAD):
        day = date.today() + timedelta(days=day_offset)

        entrance_local = (
            datetime.combine(day, lateness_config.expected_entrance_time)
            + timedelta(minutes=entrance_offset_minutes(lateness_config))
        ).time()
        entrance_at = to_utc(day, entrance_local, lateness_config.utc_offset_minutes)

        exit_local = (
            datetime.combine(day, lateness_config.expected_entrance_time)
            + timedelta(hours=8, minutes=random.randint(0, 45))
        ).time()
        exit_at = to_utc(day, exit_local, lateness_config.utc_offset_minutes)

        jitter = lambda: random.uniform(-0.01, 0.01)
        journeys.append(
            JourneyRegistry(
                user=user,
                timestamp=entrance_at,
                latitude=BASE_LATITUDE + jitter(),
                longitude=BASE_LONGITUDE + jitter(),
                selfie_id=f"mock/selfies/{user.id}_{uuid4().hex}.jpg",
            )
        )
        journeys.append(
            JourneyRegistry(
                user=user,
                timestamp=exit_at,
                latitude=BASE_LATITUDE + jitter(),
                longitude=BASE_LONGITUDE + jitter(),
                selfie_id=f"mock/selfies/{user.id}_{uuid4().hex}.jpg",
            )
        )

    return journeys


async def run() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    try:
        password_hasher = PasswordHashCreate()

        async with in_transaction():
            roles = await seed_roles()
            lateness_config = await seed_lateness_configuration()

            all_journeys: list[JourneyRegistry] = []
            created = 0
            for i in range(1, EMPLOYEE_COUNT + 1):
                journeys = await seed_employee(i, roles[UserRole.EMPLOYEE], lateness_config, password_hasher)
                if journeys:
                    created += 1
                    all_journeys.extend(journeys)

            if all_journeys:
                await JourneyRegistry.bulk_create(all_journeys, batch_size=500)

        print(f"Seeded {created} new employees (skipped {EMPLOYEE_COUNT - created} already present).")
        print(f"Login pattern: username='{USERNAME_PREFIX}NNN' (001-100), password='{DEFAULT_PASSWORD}'.")
        print(f"Journeys seeded for the next {JOURNEY_DAYS_AHEAD} days ({len(all_journeys)} registries).")
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(run())
