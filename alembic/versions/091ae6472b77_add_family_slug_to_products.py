"""add family slug to products

Revision ID: 091ae6472b77
Revises: f0e042cd176f
Create Date: 2026-05-01 15:36:47.010389

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "091ae6472b77"
down_revision: Union[str, Sequence[str], None] = "f0e042cd176f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add product family slug and backfill existing SmartBudget SKUs."""

    op.add_column(
        "products",
        sa.Column("family_slug", sa.String(length=100), nullable=True),
    )

    op.execute(
        """
        UPDATE products
        SET family_slug = 'smartbudget'
        WHERE slug LIKE 'smartbudget%'
        """
    )

    op.alter_column(
        "products",
        "family_slug",
        existing_type=sa.String(length=100),
        nullable=False,
    )

    op.create_index(
        "ix_products_family_slug",
        "products",
        ["family_slug"],
        unique=False,
    )


def downgrade() -> None:
    """Remove product family slug."""

    op.drop_index("ix_products_family_slug", table_name="products")
    op.drop_column("products", "family_slug")