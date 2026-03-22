from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.sql import get_db
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogResponse

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("", response_model=list[AuditLogResponse])
def list_activities(db: Session = Depends(get_db), admin=Depends(require_admin)):
    logs = db.scalars(select(AuditLog).order_by(AuditLog.occurred_at.desc())).all()
    return logs
