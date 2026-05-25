"""Add business foundation fields and tables

Revision ID: f3a1c9d2b4ef
Revises: 9a6f5a0b7c11
Create Date: 2026-05-23 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f3a1c9d2b4ef"
down_revision: Union[str, Sequence[str], None] = "9a6f5a0b7c11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=20), nullable=False, server_default="author"))
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    op.add_column("users", sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("deleted_at", sa.DateTime(), nullable=True))

    op.add_column("posts", sa.Column("moderation_status", sa.String(length=20), nullable=False, server_default="pending"))
    op.add_column("posts", sa.Column("moderation_reason", sa.String(), nullable=True))
    op.add_column("posts", sa.Column("moderated_by_id", sa.String(), nullable=True))
    op.add_column("posts", sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    op.add_column("posts", sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("posts", sa.Column("deleted_at", sa.DateTime(), nullable=True))

    op.add_column("categories", sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    op.add_column("categories", sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("categories", sa.Column("deleted_at", sa.DateTime(), nullable=True))

    op.add_column("locations", sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    op.add_column("locations", sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("locations", sa.Column("deleted_at", sa.DateTime(), nullable=True))

    op.add_column("comments", sa.Column("moderation_status", sa.String(length=20), nullable=False, server_default="pending"))
    op.add_column("comments", sa.Column("moderation_reason", sa.String(), nullable=True))
    op.add_column("comments", sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    op.add_column("comments", sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("comments", sa.Column("deleted_at", sa.DateTime(), nullable=True))

    op.create_table(
        "post_images",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("post_id", sa.String(), nullable=False),
        sa.Column("file_key", sa.String(length=512), nullable=False),
        sa.Column("file_url", sa.String(length=1024), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_post_images_post_id"), "post_images", ["post_id"], unique=False)

    op.create_table(
        "comment_images",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("comment_id", sa.String(), nullable=False),
        sa.Column("file_key", sa.String(length=512), nullable=False),
        sa.Column("file_url", sa.String(length=1024), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comment_images_comment_id"), "comment_images", ["comment_id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("actor_id", sa.String(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=100), nullable=False),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("before_state", sa.JSON(), nullable=True),
        sa.Column("after_state", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_index(op.f("ix_comment_images_comment_id"), table_name="comment_images")
    op.drop_table("comment_images")
    op.drop_index(op.f("ix_post_images_post_id"), table_name="post_images")
    op.drop_table("post_images")

    op.drop_column("comments", "deleted_at")
    op.drop_column("comments", "is_deleted")
    op.drop_column("comments", "updated_at")
    op.drop_column("comments", "moderation_reason")
    op.drop_column("comments", "moderation_status")

    op.drop_column("locations", "deleted_at")
    op.drop_column("locations", "is_deleted")
    op.drop_column("locations", "updated_at")

    op.drop_column("categories", "deleted_at")
    op.drop_column("categories", "is_deleted")
    op.drop_column("categories", "updated_at")

    op.drop_column("posts", "deleted_at")
    op.drop_column("posts", "is_deleted")
    op.drop_column("posts", "updated_at")
    op.drop_column("posts", "moderated_by_id")
    op.drop_column("posts", "moderation_reason")
    op.drop_column("posts", "moderation_status")

    op.drop_column("users", "deleted_at")
    op.drop_column("users", "is_deleted")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "role")
