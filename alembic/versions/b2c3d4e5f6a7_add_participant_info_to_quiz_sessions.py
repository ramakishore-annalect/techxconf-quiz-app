"""add_participant_info_to_quiz_sessions

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-10-30 01:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add participant_name and participant_mobile columns to quiz_sessions table
    op.add_column(
        "quiz_sessions", sa.Column("participant_name", sa.String(100), nullable=True)
    )
    op.add_column(
        "quiz_sessions", sa.Column("participant_mobile", sa.String(15), nullable=True)
    )

    # Add index on participant_mobile for faster lookups
    op.create_index(
        "idx_quiz_sessions_participant_mobile", "quiz_sessions", ["participant_mobile"]
    )


def downgrade() -> None:
    # Remove index and columns
    op.drop_index("idx_quiz_sessions_participant_mobile", "quiz_sessions")
    op.drop_column("quiz_sessions", "participant_mobile")
    op.drop_column("quiz_sessions", "participant_name")
