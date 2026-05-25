from datetime import datetime
from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import Base
from src.core.exceptions import DatabaseError
from src.core.pagination import PaginationParams

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    def _base_query(self, include_deleted: bool = False) -> Select[tuple[T]]:
        query = select(self.model)
        if not include_deleted and hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted.is_(False))
        return query

    async def get(self, obj_id: Any, include_deleted: bool = False) -> Optional[T]:
        try:
            query = self._base_query(include_deleted=include_deleted).where(
                self.model.id == obj_id
            )
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError(str(e))

    async def get_all(self, include_deleted: bool = False) -> Sequence[T]:
        try:
            query = self._base_query(include_deleted=include_deleted)
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError(str(e))

    async def get_page(
        self,
        pagination: PaginationParams,
        query: Select[tuple[T]] | None = None,
    ) -> tuple[Sequence[T], int]:
        try:
            current_query = query or self._base_query()
            total_query = select(func.count()).select_from(current_query.subquery())
            total_result = await self.session.execute(total_query)
            total = int(total_result.scalar_one())

            items_query = current_query.offset(pagination.offset).limit(pagination.size)
            items_result = await self.session.execute(items_query)
            return items_result.scalars().all(), total
        except SQLAlchemyError as e:
            raise DatabaseError(str(e))

    async def create(self, data: dict) -> T:
        try:
            db_obj = self.model(**data)
            self.session.add(db_obj)
            await self.session.flush()
            await self.session.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            raise DatabaseError(str(e))

    async def update(self, db_obj: T, update_data: dict) -> T:
        try:
            for field in update_data:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, update_data[field])

            self.session.add(db_obj)
            await self.session.flush()
            return db_obj
        except SQLAlchemyError as e:
            raise DatabaseError(str(e))

    async def delete(self, db_obj: T) -> None:
        try:
            if hasattr(db_obj, "is_deleted"):
                db_obj.is_deleted = True
                if hasattr(db_obj, "deleted_at"):
                    db_obj.deleted_at = datetime.utcnow()
                self.session.add(db_obj)
            else:
                await self.session.delete(db_obj)
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError(str(e))
