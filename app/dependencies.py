from typing import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from .db import SessionLocal
from . import models
from .security import decode_access_token, TokenPayload

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(decode_access_token),
):
    user = db.query(models.User).filter(models.User.id == token.sub).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user