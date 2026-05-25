from sqlalchemy.ext.asyncio import AsyncSession

from src.models.posts import AuditLog
from src.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(AuditLog, session)
