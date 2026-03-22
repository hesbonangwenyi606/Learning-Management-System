import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.user import User


def record_audit_log(
    db: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: str,
    details: dict[str, Any] | str,
    user: User | None = None,
) -> None:
    log = AuditLog(
        user_id=user.id if user else None,
        user_email=user.email if user else None,
        role=user.role.value if user else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details if isinstance(details, str) else json.dumps(details),
    )
    db.add(log)
    db.commit()
