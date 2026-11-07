import hashlib
import secrets
from datetime import datetime, timezone
from typing import Optional

from fastapi import Header, HTTPException, status

from app.shared.db.models import TirolesaDevice, TirolesaDeviceHour


def hash_device_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def generate_device_key() -> tuple[str, str]:
    """Return (plain_key, key_hash). The plain key is shown once and never stored."""
    key = secrets.token_urlsafe(32)
    return key, hash_device_key(key)


async def get_current_device(x_device_key: Optional[str] = Header(default=None)) -> TirolesaDevice:
    """Authenticate a device by its key and record that it was seen."""
    device = None
    if x_device_key:
        device = await TirolesaDevice.get_or_none(api_key_hash=hash_device_key(x_device_key))
    if device is None or not device.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid device key")

    now = datetime.now(timezone.utc)
    device.last_seen_at = now
    device.offline = False
    await device.save(update_fields=["last_seen_at", "offline"])
    await TirolesaDeviceHour.get_or_create(
        device=device,
        hour=now.replace(minute=0, second=0, microsecond=0),
    )
    return device
