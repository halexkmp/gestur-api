from uuid import UUID
from fastapi import HTTPException, status
from app.shared.db.enums import UserRole


def ensure_hr(current_user):
    """Ensure the current user has the Human Resources role.

    Raises HTTP 403 if the role is missing.
    """
    roles = current_user.roles
    if not any(getattr(r, "name", None) == UserRole.HUMAN_RESOURCES for r in roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: HR role required")

def ensure_employee(current_user):
    """Ensure the current user has the Employee role.

    Raises HTTP 403 if the role is missing.
    """
    roles = current_user.roles
    if not any(getattr(r, "name", None) == UserRole.EMPLOYEE for r in roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Employee role required")

def ensure_admin(current_user):
    """Ensure the current user has the Admin role."""
    roles = current_user.roles
    if not any(getattr(r, "name", None) == UserRole.ADMIN for r in roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Admin role required")

def ensure_hr_or_admin(current_user):
    """Ensure the current user has the Human Resources or Admin role.

    Raises HTTP 403 if neither role is present.
    """
    roles = current_user.roles
    if not any(getattr(r, "name", None) in (UserRole.HUMAN_RESOURCES, UserRole.ADMIN) for r in roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: HR or Admin role required")

def resolve_own_employee_id(current_user) -> UUID:
    """Ensure the current user has the Employee role and a linked Employee record.

    Returns the caller's own Employee id, resolved from the token — never from a
    client-supplied parameter. Raises HTTP 403 if the role or the link is missing.
    """
    ensure_employee(current_user)
    employee = current_user.employee
    if employee is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: no linked employee record")
    return employee.id
