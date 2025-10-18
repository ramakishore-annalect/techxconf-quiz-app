"""add_unique_constraint_question_text_topic

Revision ID: d88189cf8f26
Revises: 1ad30fbe84ef
Create Date: 2025-10-18 02:00:59.924029

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d88189cf8f26"
down_revision = "1ad30fbe84ef"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add unique constraint to prevent duplicate questions
    op.create_index(
        "idx_unique_question_per_topic",
        "questions",
        ["question_text", "topic"],
        unique=True,
    )


def downgrade() -> None:
    # Remove unique constraint
    op.drop_index("idx_unique_question_per_topic", "questions")
