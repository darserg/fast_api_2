import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncIterator, Dict

from fastapi import HTTPException
from sqlalchemy import JSON, Boolean, DateTime, MetaData, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings
from src.core.exceptions import DatabaseError


class PostgresDatabase:
    def __init__(self) -> None:
        self._engine = create_async_engine(settings.postgres_url)
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

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


database = PostgresDatabase()
metadata = MetaData(schema=settings.POSTGRES_SCHEMA)


class Base(DeclarativeBase):
    metadata = metadata
    type_annotation_map = {
        str: String().with_variant(String(255), "postgresql"),
        uuid.UUID: UUID(as_uuid=True),
        Dict[str, Any]: JSON,
        datetime: DateTime(timezone=True),
        bool: Boolean,
    }
