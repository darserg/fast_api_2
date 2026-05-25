from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.posts import Category
from src.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(Category, session)

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        query = self._base_query().where(Category.slug == slug)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_published(self) -> Sequence[Category]:
        query = (
            self._base_query()
            .where(Category.is_published.is_(True))
            .order_by(Category.title.asc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()
