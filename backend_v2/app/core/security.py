# backend_v2/app/core/security.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from app.config import settings
from typing import Any

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hashes a plain-text password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT Token Handling ---
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Creates a new JWT access token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Ensure the 'sub' claim (user ID) is a string
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
        
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decodes a JWT token.
    Returns the payload if successful, None otherwise.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

