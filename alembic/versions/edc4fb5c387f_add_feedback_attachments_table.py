"""add feedback_attachments table

Revision ID: edc4fb5c387f
Revises: 45d2ff51fe07
Create Date: 2026-03-30 19:56:56.927052

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'edc4fb5c387f'
down_revision: Union[str, Sequence[str], None] = '45d2ff51fe07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "feedback_attachments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("feedback_id", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("storage_type", sa.String(length=20), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["feedback_id"],
            ["feedback_messages.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_index(
        "ix_feedback_attachments_feedback_id",
        "feedback_attachments",
        ["feedback_id"],
    )

    op.create_index(
        "ix_feedback_attachments_storage_key",
        "feedback_attachments",
        ["storage_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_feedback_attachments_storage_key",
        table_name="feedback_attachments",
    )

    op.drop_index(
        "ix_feedback_attachments_feedback_id",
        table_name="feedback_attachments",
    )

    op.drop_table("feedback_attachments")
