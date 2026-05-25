import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncIterator, Dict

from fastapi import HTTPException
from sqlalchemy import JSON, Boolean, DateTime, MetaData, String
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings
from src.core.exceptions import DatabaseError


class Database:
    def __init__(self) -> None:
        self._engine: AsyncEngine = create_async_engine(settings.database_url)
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except HTTPException:
                raise
            except (Exception, PendingRollbackError) as error:
                await session.rollback()
                raise DatabaseError(message=repr(error))
            finally:
                await session.close()


database = Database()
metadata = MetaData()


class Base(DeclarativeBase):
    metadata = metadata
    type_annotation_map = {
        str: String(),
        uuid.UUID: String(),
        dict: JSON,
        Dict[str, Any]: JSON,
        datetime: DateTime(),
        bool: Boolean,
    }


async def init_models():
    async with database.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
