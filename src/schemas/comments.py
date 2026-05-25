import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.core.enums import ModerationStatus, SortOrder
from src.schemas.posts import ImageResponse


class CommentBase(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class CommentCreate(CommentBase):
    image_keys: list[str] = Field(default_factory=list)


class CommentUpdate(BaseModel):
    text: Optional[str] = Field(default=None, min_length=1, max_length=2000)
    image_keys: Optional[list[str]] = None


class CommentModerationUpdate(BaseModel):
    moderation_status: ModerationStatus
    moderation_reason: str | None = None


class CommentListFilters(BaseModel):
    moderation_status: ModerationStatus | None = None
    sort_by: str = "created_at"
    sort_order: SortOrder = SortOrder.ASC


class CommentResponse(CommentBase):
    id: str
    post_id: str
    author_id: str
    images: list[ImageResponse] = Field(default_factory=list)
    moderation_status: ModerationStatus = ModerationStatus.PENDING
    moderation_reason: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
