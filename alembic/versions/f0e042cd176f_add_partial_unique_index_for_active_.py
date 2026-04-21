"""add partial unique index for active product price

Revision ID: f0e042cd176f
Revises: ee5477ce1cbd
Create Date: 2026-04-21 20:48:01.463147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0e042cd176f'
down_revision: Union[str, Sequence[str], None] = 'ee5477ce1cbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "uq_product_price_active_per_currency",
        "product_prices",
        ["product_id", "currency_code"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "uq_product_price_active_per_currency",
        table_name="product_prices",
    )
