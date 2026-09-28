import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from app.core.config import settings

def get_password_hash(password: str) -> str:
    # Use SHA-256 with secret salt for fast, reliable, zero-dep password hashing
    key = settings.SECRET_KEY.encode('utf-8')
    msg = password.encode('utf-8')
    return hmac.new(key, msg, hashlib.sha256).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if plain_password == hashed_password:
        return True
    calculated = get_password_hash(plain_password)
    return hmac.compare_digest(calculated, hashed_password)

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
