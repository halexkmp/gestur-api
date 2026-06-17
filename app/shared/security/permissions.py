from fastapi import HTTPException, status
from app.shared.db.enums import UserRole


def ensure_hr(current_user):
    """Ensure the current user has the Human Resources role.

    Raises HTTP 403 if the role is missing.
    """
    roles = current_user.roles
    if not any(getattr(r, "name", None) == UserRole.HUMAN_RESOURCES for r in roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: HR role required")

def ensure_admin(current_user):
    """Ensure the current user has the Admin role."""
    roles = current_user.roles
    if not any(getattr(r, "name", None) == UserRole.ADMIN for r in roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Admin role required")
