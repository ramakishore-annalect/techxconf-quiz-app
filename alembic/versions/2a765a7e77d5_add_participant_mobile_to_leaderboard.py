"""add_participant_mobile_to_leaderboard

Revision ID: 2a765a7e77d5
Revises: b2c3d4e5f6a7
Create Date: 2025-10-30 03:35:14.807096

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2a765a7e77d5"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add participant_mobile column to leaderboard table
    op.add_column(
        "leaderboard",
        sa.Column("participant_mobile", sa.String(length=15), nullable=True),
    )


def downgrade() -> None:
    # Remove participant_mobile column from leaderboard table
    op.drop_column("leaderboard", "participant_mobile")
