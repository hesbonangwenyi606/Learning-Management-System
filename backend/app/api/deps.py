from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.sql import get_db
from app.models.user import User, UserRole


def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.replace("Bearer ", "", 1)
    payload = decode_token(token)
    user = db.scalar(select(User).where(User.id == int(payload["sub"])))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


def require_learner(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.LEARNER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Learner access required")
    return user
