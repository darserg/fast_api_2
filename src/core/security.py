from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    return _create_token(data, expires_delta, "access")


def create_refresh_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT refresh token."""
    return _create_token(data, expires_delta, "refresh")


def _create_token(
    data: dict,
    expires_delta: Optional[timedelta],
    token_type: str,
) -> str:
    """Create a JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire, "type": token_type})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_token(token: str, expected_type: str = "access") -> Optional[str]:
    """Verify a JWT token and return username."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        token_type: str = payload.get("type")
        if token_type != expected_type:
            return None
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None
