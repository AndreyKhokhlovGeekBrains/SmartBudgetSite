"""make sale product nullable

Revision ID: 53dee3c056fc
Revises: 91dfe4d46188
Create Date: 2026-05-15 18:23:53.487409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53dee3c056fc'
down_revision: Union[str, Sequence[str], None] = '91dfe4d46188'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "sales",
        "product_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "sales",
        "product_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )
    # ### end Alembic commands ###
