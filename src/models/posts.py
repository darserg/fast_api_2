import uuid
from datetime import datetime

from sqlalchemy import Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base
from src.core.enums import ModerationStatus


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(
        String(), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(255))
    text: Mapped[str]
    pub_date: Mapped[datetime]
    is_published: Mapped[bool] = mapped_column(default=True)
    author_id: Mapped[str] = mapped_column(String())
    category_id: Mapped[str] = mapped_column(String(), nullable=True)
    location_id: Mapped[str] = mapped_column(String(), nullable=True)
    image: Mapped[str] = mapped_column(String(), nullable=True)
    moderation_status: Mapped[str] = mapped_column(
        String(20), default=ModerationStatus.PENDING.value, nullable=False
    )
    moderation_reason: Mapped[str | None] = mapped_column(nullable=True)
    moderated_by_id: Mapped[str | None] = mapped_column(String(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)
    comment_count: Mapped[int] = mapped_column(nullable=True)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(
        String(), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str]
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_published: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[str] = mapped_column(
        String(), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_published: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(
        String(), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    post_id: Mapped[str] = mapped_column(String(), index=True)
    author_id: Mapped[str] = mapped_column(String(), index=True)
    text: Mapped[str]
    moderation_status: Mapped[str] = mapped_column(
        String(20), default=ModerationStatus.PENDING.value, nullable=False
    )
    moderation_reason: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)


class PostImage(Base):
    __tablename__ = "post_images"

    id: Mapped[str] = mapped_column(
        String(), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    post_id: Mapped[str] = mapped_column(String(), index=True)
    file_key: Mapped[str] = mapped_column(String(512), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class CommentImage(Base):
    __tablename__ = "comment_images"

    id: Mapped[str] = mapped_column(
        String(), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    comment_id: Mapped[str] = mapped_column(String(), index=True)
    file_key: Mapped[str] = mapped_column(String(512), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    actor_id: Mapped[str | None] = mapped_column(String(), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    before_state: Mapped[dict | None] = mapped_column(nullable=True)
    after_state: Mapped[dict | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
