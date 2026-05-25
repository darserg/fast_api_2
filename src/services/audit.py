from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi import Request

from src.repositories.audit import AuditRepository


class AuditService:
    def __init__(self, audit_repo: AuditRepository, request: Request) -> None:
        self.audit_repo = audit_repo
        self.request = request

    async def log(
        self,
        *,
        actor_id: str | None,
        action: str,
        entity_type: str,
        entity_id: str,
        before_state: dict[str, Any] | None = None,
        after_state: dict[str, Any] | None = None,
    ) -> None:
        await self.audit_repo.create(
            {
                "actor_id": actor_id,
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "request_id": getattr(self.request.state, "request_id", None),
                "before_state": jsonable_encoder(before_state) if before_state else None,
                "after_state": jsonable_encoder(after_state) if after_state else None,
            }
        )
