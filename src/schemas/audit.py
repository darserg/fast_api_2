from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: str
    actor_id: str | None
    action: str
    entity_type: str
    entity_id: str
    request_id: str | None
    before_state: dict[str, Any] | None = None
    after_state: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
