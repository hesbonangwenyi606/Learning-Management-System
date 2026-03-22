from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_email: str | None
    role: str | None
    action: str
    entity_type: str
    entity_id: str
    details: str
    occurred_at: datetime
