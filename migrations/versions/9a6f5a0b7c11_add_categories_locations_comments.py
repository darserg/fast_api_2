"""Add categories, locations and comments tables

Revision ID: 9a6f5a0b7c11
Revises: be605aea953f
Create Date: 2026-05-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9a6f5a0b7c11"
down_revision: Union[str, Sequence[str], None] = "be605aea953f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_categories_slug"), "categories", ["slug"], unique=True)

    op.create_table(
        "locations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "comments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("post_id", sa.String(), nullable=False),
        sa.Column("author_id", sa.String(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comments_author_id"), "comments", ["author_id"], unique=False)
    op.create_index(op.f("ix_comments_post_id"), "comments", ["post_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_comments_post_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_author_id"), table_name="comments")
    op.drop_table("comments")
    op.drop_table("locations")
    op.drop_index(op.f("ix_categories_slug"), table_name="categories")
    op.drop_table("categories")
