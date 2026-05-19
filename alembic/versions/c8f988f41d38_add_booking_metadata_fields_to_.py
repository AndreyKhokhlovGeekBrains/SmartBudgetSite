"""add booking metadata fields to consultation entitlements

Revision ID: c8f988f41d38
Revises: c8093cf7f44a
Create Date: 2026-05-19 20:23:02.499243

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c8f988f41d38'
down_revision: Union[str, Sequence[str], None] = 'c8093cf7f44a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "consultation_entitlements",
        sa.Column("booking_provider", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "consultation_entitlements",
        sa.Column("provider_event_uri", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "consultation_entitlements",
        sa.Column("provider_invitee_uri", sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("consultation_entitlements", "provider_invitee_uri")
    op.drop_column("consultation_entitlements", "provider_event_uri")
    op.drop_column("consultation_entitlements", "booking_provider")
