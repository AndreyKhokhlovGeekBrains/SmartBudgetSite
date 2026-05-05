"""seed smartbudget int standard product

Revision ID: 0e18f750c678
Revises: e0418a7913dc
Create Date: 2026-05-05 21:15:23.152161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e18f750c678'
down_revision: Union[str, Sequence[str], None] = 'e0418a7913dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute(
        """
        INSERT INTO products (
            family_slug,
            slug,
            name,
            archive_path,
            edition,
            version,
            status
        )
        VALUES (
            'smartbudget',
            'smartbudget-int-standard',
            'SmartBudget',
            '',
            'Standard',
            '1.0',
            'in_sale'
        )
        ON CONFLICT (slug) DO NOTHING;
        """
    )

    op.execute(
        """
        INSERT INTO product_prices (
            product_id,
            currency_code,
            amount,
            is_active
        )
        SELECT
            p.id,
            'EUR',
            39.00,
            true
        FROM products AS p
        WHERE p.slug = 'smartbudget-int-standard'
          AND NOT EXISTS (
              SELECT 1
              FROM product_prices AS pp
              WHERE pp.product_id = p.id
                AND pp.currency_code = 'EUR'
                AND pp.is_active = true
          );
        """
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.execute(
        """
        DELETE FROM product_prices
        WHERE product_id IN (
            SELECT id
            FROM products
            WHERE slug = 'smartbudget-int-standard'
        );
        """
    )

    op.execute(
        """
        DELETE FROM products
        WHERE slug = 'smartbudget-int-standard';
        """
    )
