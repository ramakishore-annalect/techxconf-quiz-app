"""Excel import service."""

import io
import logging
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import Question, Answer, Difficulty, CorrectOption
from app.schemas.question import (
    QuestionCreate,
    AnswerCreate,
    QuestionWithAnswer,
    ImportResult,
    ImportError,
    ImportValidationResult
)

logger = logging.getLogger(__name__)


class ExcelImportService:
    """Excel import service for questions and answers."""

    # Expected column names for Questions sheet
    QUESTIONS_COLUMNS = {
        'ID': 'id',
        'Topic': 'topic',
        'Difficulty': 'difficulty',
        'Question': 'question_text',
        'Option A': 'option_a',
        'Option B': 'option_b',
        'Option C': 'option_c',
        'Option D': 'option_d'
    }

    # Expected column names for Answers sheet
    ANSWERS_COLUMNS = {
        'ID': 'id',
        'Correct Option': 'correct_option',
        'Correct Answer Text': 'correct_text',
        'Short Explanation': 'explanation'
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def import_from_excel(
        self,
        file_content: bytes,
        created_by_id: Optional[UUID] = None,
        mode: str = "upsert"  # "upsert", "replace", "preview"
    ) -> ImportResult:
        """Import questions and answers from Excel file."""
        logger.info(f"Starting Excel import with mode: {mode}")

        try:
            # Validate and parse Excel file
            validation_result = self._validate_excel_file(file_content)
            if not validation_result.is_valid:
                return ImportResult(
                    total_rows=0,
                    processed_questions=0,
                    processed_answers=0,
                    created_questions=0,
                    updated_questions=0,
                    skipped_questions=len(validation_result.errors),
                    errors=[self._error_to_dict(error) for error in validation_result.errors],
                    warnings=[self._error_to_dict(warning) for warning in validation_result.warnings]
                )

            if mode == "preview":
                return ImportResult(
                    total_rows=len(validation_result.questions_data),
                    processed_questions=len(validation_result.questions_data),
                    processed_answers=len(validation_result.questions_data),
                    created_questions=0,
                    updated_questions=0,
                    skipped_questions=0,
                    errors=[],
                    warnings=[self._error_to_dict(warning) for warning in validation_result.warnings]
                )

            # Process the validated data
            return await self._process_questions(
                validation_result.questions_data,
                created_by_id,
                mode,
                validation_result.warnings
            )

        except Exception as e:
            logger.error(f"Excel import failed: {str(e)}")
            return ImportResult(
                total_rows=0,
                processed_questions=0,
                processed_answers=0,
                created_questions=0,
                updated_questions=0,
                skipped_questions=0,
                errors=[{
                    "row_number": 0,
                    "field": "file",
                    "error_message": f"Failed to process file: {str(e)}"
                }],
                warnings=[]
            )

    def _validate_excel_file(self, file_content: bytes) -> ImportValidationResult:
        """Validate Excel file structure and content."""
        errors = []
        warnings = []
        questions_data = []

        try:
            # Read Excel file
            excel_file = io.BytesIO(file_content)
            excel_data = pd.read_excel(excel_file, sheet_name=None)

            # Check required sheets
            if "Questions" not in excel_data:
                errors.append(ImportError(
                    row_number=0,
                    field="sheet",
                    error_message="Missing 'Questions' sheet"
                ))

            if "Answers" not in excel_data:
                errors.append(ImportError(
                    row_number=0,
                    field="sheet",
                    error_message="Missing 'Answers' sheet"
                ))

            if errors:
                return ImportValidationResult(
                    is_valid=False,
                    questions_data=[],
                    errors=errors,
                    warnings=warnings
                )

            questions_df = excel_data["Questions"]
            answers_df = excel_data["Answers"]

            # Validate columns
            questions_errors = self._validate_sheet_columns(
                questions_df, self.QUESTIONS_COLUMNS, "Questions"
            )
            answers_errors = self._validate_sheet_columns(
                answers_df, self.ANSWERS_COLUMNS, "Answers"
            )

            errors.extend(questions_errors)
            errors.extend(answers_errors)

            if errors:
                return ImportValidationResult(
                    is_valid=False,
                    questions_data=[],
                    errors=errors,
                    warnings=warnings
                )

            # Validate and parse data
            questions_data, parse_errors, parse_warnings = self._parse_and_validate_data(
                questions_df, answers_df
            )

            errors.extend(parse_errors)
            warnings.extend(parse_warnings)

            return ImportValidationResult(
                is_valid=len(errors) == 0,
                questions_data=questions_data,
                errors=errors,
                warnings=warnings
            )

        except Exception as e:
            errors.append(ImportError(
                row_number=0,
                field="file",
                error_message=f"Failed to read Excel file: {str(e)}"
            ))

            return ImportValidationResult(
                is_valid=False,
                questions_data=[],
                errors=errors,
                warnings=warnings
            )

    def _validate_sheet_columns(
        self,
        df: pd.DataFrame,
        expected_columns: Dict[str, str],
        sheet_name: str
    ) -> List[ImportError]:
        """Validate sheet has required columns."""
        errors = []
        df_columns = list(df.columns)

        for expected_col in expected_columns.keys():
            if expected_col not in df_columns:
                errors.append(ImportError(
                    row_number=0,
                    field="columns",
                    error_message=f"Missing required column '{expected_col}' in {sheet_name} sheet"
                ))

        return errors

    def _parse_and_validate_data(
        self,
        questions_df: pd.DataFrame,
        answers_df: pd.DataFrame
    ) -> Tuple[List[QuestionWithAnswer], List[ImportError], List[ImportError]]:
        """Parse and validate data from both sheets."""
        questions_data = []
        errors = []
        warnings = []

        # Convert to dictionaries for easier processing
        questions_dict = {}
        answers_dict = {}

        # Process Questions sheet
        for idx, row in questions_df.iterrows():
            row_num = idx + 2  # Excel row number (1-indexed + header row)

            try:
                # Check for required fields
                question_id = row.get('ID')
                if pd.isna(question_id) or question_id == '':
                    errors.append(ImportError(
                        row_number=row_num,
                        field="ID",
                        error_message="Missing ID"
                    ))
                    continue

                question_id = int(question_id)

                # Validate difficulty
                difficulty_str = str(row.get('Difficulty', '')).lower().strip()
                if difficulty_str not in ['easy', 'medium', 'hard']:
                    errors.append(ImportError(
                        row_number=row_num,
                        field="Difficulty",
                        error_message=f"Invalid difficulty '{difficulty_str}'. Must be 'easy', 'medium', or 'hard'"
                    ))
                    continue

                # Create question data
                question_data = QuestionCreate(
                    original_xls_id=question_id,
                    topic=str(row.get('Topic', '')).strip(),
                    difficulty=Difficulty(difficulty_str),
                    question_text=str(row.get('Question', '')).strip(),
                    option_a=str(row.get('Option A', '')).strip(),
                    option_b=str(row.get('Option B', '')).strip(),
                    option_c=str(row.get('Option C', '')).strip(),
                    option_d=str(row.get('Option D', '')).strip(),
                )

                questions_dict[question_id] = {
                    'row_number': row_num,
                    'question': question_data
                }

            except ValueError as e:
                errors.append(ImportError(
                    row_number=row_num,
                    field="validation",
                    error_message=str(e)
                ))
            except Exception as e:
                errors.append(ImportError(
                    row_number=row_num,
                    field="processing",
                    error_message=f"Error processing row: {str(e)}"
                ))

        # Process Answers sheet
        for idx, row in answers_df.iterrows():
            row_num = idx + 2  # Excel row number (1-indexed + header row)

            try:
                answer_id = row.get('ID')
                if pd.isna(answer_id) or answer_id == '':
                    errors.append(ImportError(
                        row_number=row_num,
                        field="ID",
                        error_message="Missing ID"
                    ))
                    continue

                answer_id = int(answer_id)

                # Validate correct option
                correct_option_str = str(row.get('Correct Option', '')).strip().upper()
                if correct_option_str not in ['A', 'B', 'C', 'D']:
                    errors.append(ImportError(
                        row_number=row_num,
                        field="Correct Option",
                        error_message=f"Invalid correct option '{correct_option_str}'. Must be A, B, C, or D"
                    ))
                    continue

                # Create answer data
                answer_data = AnswerCreate(
                    correct_option=CorrectOption(correct_option_str),
                    correct_text=str(row.get('Correct Answer Text', '')).strip(),
                    explanation=str(row.get('Short Explanation', '')).strip() or None
                )

                answers_dict[answer_id] = {
                    'row_number': row_num,
                    'answer': answer_data
                }

            except ValueError as e:
                errors.append(ImportError(
                    row_number=row_num,
                    field="validation",
                    error_message=str(e)
                ))
            except Exception as e:
                errors.append(ImportError(
                    row_number=row_num,
                    field="processing",
                    error_message=f"Error processing row: {str(e)}"
                ))

        # Match questions with answers
        for question_id in questions_dict:
            if question_id not in answers_dict:
                errors.append(ImportError(
                    row_number=questions_dict[question_id]['row_number'],
                    field="matching",
                    error_message=f"No corresponding answer found for question ID {question_id}"
                ))
                continue

            question_item = questions_dict[question_id]
            answer_item = answers_dict[question_id]

            try:
                # Create combined question-answer object
                question_with_answer = QuestionWithAnswer(
                    question=question_item['question'],
                    answer=answer_item['answer']
                )

                # Validate that answer matches question options
                question_with_answer.validate_answer_matches_option()

                questions_data.append(question_with_answer)

            except ValueError as e:
                errors.append(ImportError(
                    row_number=question_item['row_number'],
                    field="validation",
                    error_message=str(e)
                ))

        # Check for answers without questions
        for answer_id in answers_dict:
            if answer_id not in questions_dict:
                warnings.append(ImportError(
                    row_number=answers_dict[answer_id]['row_number'],
                    field="matching",
                    error_message=f"Answer ID {answer_id} has no corresponding question"
                ))

        return questions_data, errors, warnings

    async def _process_questions(
        self,
        questions_data: List[QuestionWithAnswer],
        created_by_id: Optional[UUID],
        mode: str,
        warnings: List[ImportError]
    ) -> ImportResult:
        """Process validated questions data."""
        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []

        for question_with_answer in questions_data:
            try:
                # Check if question already exists (by original_xls_id)
                existing_question = None
                if question_with_answer.question.original_xls_id:
                    result = await self.db.execute(
                        select(Question).where(
                            Question.original_xls_id == question_with_answer.question.original_xls_id
                        )
                    )
                    existing_question = result.scalar_one_or_none()

                if existing_question:
                    if mode == "upsert":
                        # Update existing question
                        await self._update_question(existing_question, question_with_answer, created_by_id)
                        updated_count += 1
                    else:
                        skipped_count += 1
                else:
                    # Create new question
                    await self._create_question(question_with_answer, created_by_id)
                    created_count += 1

            except Exception as e:
                logger.error(f"Error processing question: {str(e)}")
                errors.append({
                    "row_number": 0,  # We don't have row numbers in this context
                    "field": "processing",
                    "error_message": f"Error processing question ID {question_with_answer.question.original_xls_id}: {str(e)}"
                })
                skipped_count += 1

        # Commit all changes
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error committing changes: {str(e)}")
            raise

        return ImportResult(
            total_rows=len(questions_data),
            processed_questions=len(questions_data),
            processed_answers=len(questions_data),
            created_questions=created_count,
            updated_questions=updated_count,
            skipped_questions=skipped_count,
            errors=errors,
            warnings=[self._error_to_dict(warning) for warning in warnings]
        )

    async def _create_question(
        self,
        question_with_answer: QuestionWithAnswer,
        created_by_id: Optional[UUID]
    ) -> Question:
        """Create a new question and answer."""
        # Create question
        question = Question(
            original_xls_id=question_with_answer.question.original_xls_id,
            topic=question_with_answer.question.topic,
            difficulty=question_with_answer.question.difficulty,
            question_text=question_with_answer.question.question_text,
            option_a=question_with_answer.question.option_a,
            option_b=question_with_answer.question.option_b,
            option_c=question_with_answer.question.option_c,
            option_d=question_with_answer.question.option_d,
            created_by=created_by_id
        )

        self.db.add(question)
        await self.db.flush()  # Get the ID

        # Create answer
        answer = Answer(
            question_id=question.id,
            correct_option=question_with_answer.answer.correct_option,
            correct_text=question_with_answer.answer.correct_text,
            explanation=question_with_answer.answer.explanation
        )

        self.db.add(answer)
        return question

    async def _update_question(
        self,
        existing_question: Question,
        question_with_answer: QuestionWithAnswer,
        created_by_id: Optional[UUID]
    ) -> Question:
        """Update an existing question and answer."""
        # Update question fields
        existing_question.topic = question_with_answer.question.topic
        existing_question.difficulty = question_with_answer.question.difficulty
        existing_question.question_text = question_with_answer.question.question_text
        existing_question.option_a = question_with_answer.question.option_a
        existing_question.option_b = question_with_answer.question.option_b
        existing_question.option_c = question_with_answer.question.option_c
        existing_question.option_d = question_with_answer.question.option_d

        # Update answer
        if existing_question.answer:
            existing_question.answer.correct_option = question_with_answer.answer.correct_option
            existing_question.answer.correct_text = question_with_answer.answer.correct_text
            existing_question.answer.explanation = question_with_answer.answer.explanation
        else:
            # Create answer if it doesn't exist
            answer = Answer(
                question_id=existing_question.id,
                correct_option=question_with_answer.answer.correct_option,
                correct_text=question_with_answer.answer.correct_text,
                explanation=question_with_answer.answer.explanation
            )
            self.db.add(answer)

        return existing_question

    def _error_to_dict(self, error: ImportError) -> Dict[str, Any]:
        """Convert ImportError to dictionary."""
        return {
            "row_number": error.row_number,
            "field": error.field,
            "error_message": error.error_message,
            "row_data": error.row_data
        }