from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserRole
from app.schemas.auth import UserLogin, UserRegister
from app.services.audit import record_audit_log


def register_learner(db: Session, payload: UserRegister) -> User:
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")

    user = User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower(),
        password_hash=get_password_hash(payload.password),
        role=UserRole.LEARNER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    record_audit_log(
        db,
        action="register",
        entity_type="user",
        entity_id=str(user.id),
        details={"message": "Learner registered"},
        user=user,
    )
    return user


def authenticate_user(db: Session, payload: UserLogin) -> User:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return user


def ensure_default_admin(db: Session, *, email: str, password: str) -> None:
    existing = db.scalar(select(User).where(User.email == email.lower()))
    if existing:
        return
    admin = User(
        full_name="System Administrator",
        email=email.lower(),
        password_hash=get_password_hash(password),
        role=UserRole.ADMIN,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    record_audit_log(
        db,
        action="seed_admin",
        entity_type="user",
        entity_id=str(admin.id),
        details={"message": "Default admin account created"},
        user=admin,
    )
