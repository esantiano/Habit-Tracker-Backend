from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict
from app.passwordhash import Hash

# used to load the secret key from .env
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return Hash.bcrypt(password)

def verify_password(plain_password: str, password_hash: str) -> bool:
    return Hash.verify(plain_password, password_hash)

class TokenPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sub: int
    exp: int

def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"sub": user_id, "exp": int(expire.timestamp())}
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
def decode_access_token(token: str) -> TokenPayload:
    from fastapi.security import OAuth2PasswordBearer

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

    async def _dependency(t: str = Depends(oauth2_scheme)) -> TokenPayload:
        try:
            payload = jwt.decode(t, SECRET_KEY, algorithms=[ALGORITHM])
            token_data = TokenPayload(**payload)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return token_data
    return _dependency(token)