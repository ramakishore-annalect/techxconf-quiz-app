"""
Remove duplicate questions from the database.
Keeps only one copy of each unique question (by question_text + topic).
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, engine
from app.models import Question, Answer, SessionAnswer


async def remove_duplicates():
    """Remove duplicate questions, keeping only one copy of each unique question."""

    async with AsyncSession(engine) as db:
        print("Finding duplicate questions...")

        # Get all questions ordered by creation (keep oldest)
        query = select(Question).order_by(Question.created_at.asc())
        result = await db.execute(query)
        all_questions = result.scalars().all()

        # Track unique questions by (question_text, topic)
        seen = set()
        duplicates_to_delete = []
        kept_count = 0

        for question in all_questions:
            key = (question.question_text.strip(), question.topic.strip())

            if key in seen:
                # This is a duplicate
                duplicates_to_delete.append(question.id)
                print(
                    f"  ❌ Duplicate found: {question.topic} - {question.question_text[:60]}..."
                )
            else:
                # Keep this one
                seen.add(key)
                kept_count += 1

        if not duplicates_to_delete:
            print("✅ No duplicates found!")
            return

        print(f"\nFound {len(duplicates_to_delete)} duplicate questions")
        print(f"Keeping {kept_count} unique questions")
        print("\nDeleting duplicates...")

        # First, delete any session answers referencing these questions
        if duplicates_to_delete:
            session_answer_delete = delete(SessionAnswer).where(
                SessionAnswer.question_id.in_(duplicates_to_delete)
            )
            result = await db.execute(session_answer_delete)
            print(
                f"  Deleted {result.rowcount} session answers referencing duplicate questions"
            )

            # Delete answers for duplicate questions
            answer_delete = delete(Answer).where(
                Answer.question_id.in_(duplicates_to_delete)
            )
            result = await db.execute(answer_delete)
            print(f"  Deleted {result.rowcount} answers for duplicate questions")

            # Delete the duplicate questions
            question_delete = delete(Question).where(
                Question.id.in_(duplicates_to_delete)
            )
            result = await db.execute(question_delete)
            print(f"  Deleted {result.rowcount} duplicate questions")

        await db.commit()

        # Verify
        verify_query = select(Question)
        result = await db.execute(verify_query)
        final_count = len(result.scalars().all())

        print(f"\n✅ Cleanup complete!")
        print(f"   Total unique questions remaining: {final_count}")
        print(f"   Duplicates removed: {len(duplicates_to_delete)}")


async def verify_no_duplicates():
    """Verify there are no more duplicates."""
    async with AsyncSession(engine) as db:
        query = select(Question)
        result = await db.execute(query)
        all_questions = result.scalars().all()

        seen = {}
        duplicates = []

        for question in all_questions:
            key = (question.question_text.strip(), question.topic.strip())
            if key in seen:
                duplicates.append((question.topic, question.question_text))
            else:
                seen[key] = question.id

        if duplicates:
            print(f"⚠️  WARNING: Still found {len(duplicates)} duplicates:")
            for topic, text in duplicates[:5]:
                print(f"  - {topic}: {text[:60]}...")
        else:
            print("✅ Verification passed: No duplicates found!")


if __name__ == "__main__":
    print("=" * 70)
    print("REMOVING DUPLICATE QUESTIONS FROM DATABASE")
    print("=" * 70)
    print()

    asyncio.run(remove_duplicates())

    print()
    print("=" * 70)
    print("VERIFYING NO DUPLICATES REMAIN")
    print("=" * 70)
    print()

    asyncio.run(verify_no_duplicates())
