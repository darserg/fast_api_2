from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings


class HealthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def check(self) -> dict:
        await self.session.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "ok",
            "environment": settings.ENVIRONMENT,
        }
