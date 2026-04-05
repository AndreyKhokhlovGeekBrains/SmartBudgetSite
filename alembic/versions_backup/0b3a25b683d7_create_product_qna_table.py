"""create product qna table

Revision ID: 0b3a25b683d7
Revises: edc4fb5c387f
Create Date: 2026-04-05 19:08:07.846737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0b3a25b683d7'
down_revision: Union[str, Sequence[str], None] = 'edc4fb5c387f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "product_qna",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("display_name", sa.String(length=100), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_product_qna_product_id", "product_qna", ["product_id"], unique=False)
    op.create_index("ix_product_qna_is_published", "product_qna", ["is_published"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index("ix_product_qna_is_published", table_name="product_qna")
    op.drop_index("ix_product_qna_product_id", table_name="product_qna")
    op.drop_table("product_qna")
    # ### end Alembic commands ###
