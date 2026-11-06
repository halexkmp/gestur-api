import secrets
from typing import Optional

from fastapi import Header, HTTPException, status

from app.config import settings


def verify_cron_secret(authorization: Optional[str] = Header(default=None)) -> None:
    """Allow only Vercel's scheduler, which sends `Authorization: Bearer <CRON_SECRET>`.

    Rejects every request when CRON_SECRET is not configured.
    """
    expected = settings.CRON_SECRET
    if not expected or not authorization or not secrets.compare_digest(
        authorization.encode(), f"Bearer {expected}".encode()
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid cron secret")
