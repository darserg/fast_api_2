from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.core.enums import ModerationStatus, SortOrder
from src.core.validators import PostValidators


class PostBase(BaseModel):
    title: str = Field(max_length=255)
    text: str
    pub_date: datetime
    is_published: bool = True


class PostCreate(PostBase, PostValidators):
    category_id: Optional[str] = None
    location_id: Optional[str] = None
    image_keys: list[str] = Field(default_factory=list)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    text: Optional[str] = None
    pub_date: Optional[datetime] = None
    is_published: Optional[bool] = None
    category_id: Optional[str] = None
    location_id: Optional[str] = None
    image_keys: Optional[list[str]] = None


class PostModerationUpdate(BaseModel):
    moderation_status: ModerationStatus
    moderation_reason: Optional[str] = None


class PostListFilters(BaseModel):
    search: Optional[str] = None
    author_id: Optional[str] = None
    category_id: Optional[str] = None
    location_id: Optional[str] = None
    is_published: Optional[bool] = None
    moderation_status: Optional[ModerationStatus] = None
    sort_by: str = "pub_date"
    sort_order: SortOrder = SortOrder.DESC


class ImageResponse(BaseModel):
    id: str
    file_key: str
    file_url: str
    position: int

    model_config = ConfigDict(from_attributes=True)


class PostResponse(PostBase):
    id: str
    author_id: str
    category_id: Optional[str]
    location_id: Optional[str]
    image: Optional[str] = None
    images: list[ImageResponse] = Field(default_factory=list)
    moderation_status: ModerationStatus = ModerationStatus.PENDING
    moderation_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    comment_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
