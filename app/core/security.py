from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings
import base64
import cryptography.fernet
import logging
import bcrypt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    logger.info(f"SECRET_KEY in create_access_token: {settings.SECRET_KEY[:20]}...")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})
    logger.info(f"Payload to encode: {to_encode}")
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.info(f"Encoded token: {encoded_jwt[:50]}...")
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    logger.info(f"SECRET_KEY in decode_access_token: {settings.SECRET_KEY[:20]}...")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        return None


def encrypt_password(password: str) -> str:
    """Encrypt a password using Fernet symmetric encryption"""
    key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode().ljust(32)[:32])
    fernet = cryptography.fernet.Fernet(key)
    encrypted = fernet.encrypt(password.encode())
    return encrypted.decode()


def decrypt_password(encrypted_password: str) -> str:
    """Decrypt a password using Fernet symmetric encryption"""
    key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode().ljust(32)[:32])
    fernet = cryptography.fernet.Fernet(key)
    decrypted = fernet.decrypt(encrypted_password.encode())
    return decrypted.decode()
