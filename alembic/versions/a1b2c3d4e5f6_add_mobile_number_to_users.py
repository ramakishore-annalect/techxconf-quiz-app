"""add_mobile_number_to_users

Revision ID: a1b2c3d4e5f6
Revises: d88189cf8f26
Create Date: 2025-10-30 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "d88189cf8f26"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add mobile_number column to users table
    op.add_column("users", sa.Column("mobile_number", sa.String(15), nullable=True))


def downgrade() -> None:
    # Remove mobile_number column from users table
    op.drop_column("users", "mobile_number")
