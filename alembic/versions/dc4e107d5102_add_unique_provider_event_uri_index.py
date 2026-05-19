"""add unique provider event uri index

Revision ID: dc4e107d5102
Revises: c8f988f41d38
Create Date: 2026-05-19 21:17:36.354305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "dc4e107d5102"
down_revision: Union[str, Sequence[str], None] = "c8f988f41d38"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "uq_consultation_entitlements_provider_event_uri",
        "consultation_entitlements",
        ["provider_event_uri"],
        unique=True,
        postgresql_where=sa.text("provider_event_uri IS NOT NULL"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "uq_consultation_entitlements_provider_event_uri",
        table_name="consultation_entitlements",
        postgresql_where=sa.text("provider_event_uri IS NOT NULL"),
    )
