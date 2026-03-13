import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str]
    text: Mapped[str]
    is_published: Mapped[bool] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    autor_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4())
    location_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4())
    image: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    comment_count: Mapped[int]