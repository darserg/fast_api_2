import uuid
from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base
from src.core.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    first_name: Mapped[str]
    last_name: Mapped[str]
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    role: Mapped[str] = mapped_column(
        String(20), default=UserRole.AUTHOR.value, nullable=False
    )
    last_login_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)
