"""add usage_type to service_addons

Revision ID: d8a835dfe21e
Revises: 0e18f750c678
Create Date: 2026-05-11 18:16:58.061690

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d8a835dfe21e"
down_revision: Union[str, Sequence[str], None] = "0e18f750c678"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "service_addons",
        sa.Column("usage_type", sa.String(length=30), nullable=True),
    )

    op.execute(
        "UPDATE service_addons SET usage_type = 'addon' WHERE usage_type IS NULL"
    )

    op.alter_column(
        "service_addons",
        "usage_type",
        existing_type=sa.String(length=30),
        nullable=False,
    )

    op.create_index(
        op.f("ix_service_addons_usage_type"),
        "service_addons",
        ["usage_type"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_service_addons_usage_type"), table_name="service_addons")
    op.drop_column("service_addons", "usage_type")