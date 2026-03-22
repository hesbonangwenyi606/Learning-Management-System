from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.db.sql import get_db
from app.schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse
from app.services.auth import authenticate_user, register_learner
from app.services.audit import record_audit_log

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    user = register_learner(db, payload)
    token = create_access_token(subject=user.id, role=user.role.value)
    return TokenResponse(access_token=token, user=user)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload)
    record_audit_log(
        db,
        action="login",
        entity_type="auth",
        entity_id=str(user.id),
        details={"message": "Successful login"},
        user=user,
    )
    token = create_access_token(subject=user.id, role=user.role.value)
    return TokenResponse(access_token=token, user=user)


@router.get("/me", response_model=UserResponse)
def get_me(user=Depends(get_current_user)):
    return user
