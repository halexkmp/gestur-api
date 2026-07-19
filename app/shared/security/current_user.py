from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.shared.db.models import User

# Simple in-memory cache for current user lookups, keyed by token
_USER_CACHE: dict[str, tuple[object, datetime]] = {}
_TTL = timedelta(hours=1)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # First, validate the token (and its claims) to ensure it is structurally valid
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Return cached user if present and not expired
    now = datetime.now(timezone.utc)
    cached = _USER_CACHE.get(token)
    if cached:
        user_obj, expires_at = cached
        if expires_at > now:
            return user_obj
        else:
            # expired cache entry
            _USER_CACHE.pop(token, None)

    # Cache miss or expired: fetch from DB
    user = await User.get_or_none(username=username).prefetch_related("roles","employee")
    if user is None:
        raise credentials_exception

    _USER_CACHE[token] = (user, now + _TTL)
    return user
