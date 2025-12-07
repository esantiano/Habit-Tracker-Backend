import hashlib
import bcrypt

MAX_BCRYPT_BYTES = 72

def _normalize(password: str) -> bytes:
    """
    Ensure the password fits bcrypt limits by pre-hashing if needed.
    """
    raw = password.encode("utf-8")
    if len(raw) > MAX_BCRYPT_BYTES:
        return hashlib.sha256(raw).digest()
    return raw


class Hash:
    @staticmethod
    def bcrypt(password: str) -> str:
        normalized = _normalize(password)
        return bcrypt.hashpw(normalized, bcrypt.gensalt()).decode()

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        normalized = _normalize(plain_password)
        return bcrypt.checkpw(normalized, hashed_password.encode())