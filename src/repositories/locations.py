from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.posts import Location
from src.repositories.base import BaseRepository


class LocationRepository(BaseRepository[Location]):
    def __init__(self, session: AsyncSession):
        super().__init__(Location, session)

    async def get_published(self) -> Sequence[Location]:
        query = (
            self._base_query()
            .where(Location.is_published.is_(True))
            .order_by(Location.name.asc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()
