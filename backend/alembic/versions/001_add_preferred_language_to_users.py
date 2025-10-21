"""Add preferred_language to users table

Revision ID: 001
Revises:
Create Date: 2025-01-20

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add preferred_language column to users table."""
    # Add the preferred_language column with a default value
    op.add_column(
        'users',
        sa.Column('preferred_language', sa.String(length=10), nullable=False, server_default='en')
    )


def downgrade() -> None:
    """Remove preferred_language column from users table."""
    op.drop_column('users', 'preferred_language')
