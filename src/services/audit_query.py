from src.core.enums import UserRole
from src.core.pagination import PaginationParams
from src.repositories.audit import AuditRepository
from src.schemas.audit import AuditLogResponse
from src.schemas.common import Page


class AuditQueryService:
    def __init__(self, audit_repo: AuditRepository) -> None:
        self.audit_repo = audit_repo

    async def list_logs(self, pagination: PaginationParams, current_user) -> Page[AuditLogResponse]:
        if current_user.role not in {UserRole.MODERATOR, UserRole.ADMIN}:
            from fastapi import HTTPException

            raise HTTPException(status_code=403, detail="Staff permissions required")
        items, total = await self.audit_repo.get_page(pagination)
        return Page(
            items=items,
            page=pagination.page,
            size=pagination.size,
            total=total,
        )
