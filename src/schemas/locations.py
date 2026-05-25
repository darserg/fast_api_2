import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LocationBase(BaseModel):
    name: str = Field(max_length=255)
    is_published: bool = True


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    is_published: Optional[bool] = None


class LocationResponse(LocationBase):
    id: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
