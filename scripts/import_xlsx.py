#!/usr/bin/env python3
"""XLSX import CLI script."""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from app.core.database import AsyncSessionLocal
from app.services.excel_import import ExcelImportService
from app.schemas.question import ImportResult


async def import_xlsx_file(
    file_path: str,
    mode: str = "upsert",
    created_by_id: str = None
) -> ImportResult:
    """Import XLSX file."""
    # Read file
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        sys.exit(1)

    # Import using service
    async with AsyncSessionLocal() as session:
        import_service = ExcelImportService(session)

        try:
            result = await import_service.import_from_excel(
                file_content,
                created_by_id=created_by_id,
                mode=mode
            )
            return result
        except Exception as e:
            print(f"Import failed: {e}")
            sys.exit(1)


def print_import_result(result: ImportResult):
    """Print import result."""
    print("\n" + "="*60)
    print("IMPORT RESULTS")
    print("="*60)

    print(f"Total rows processed: {result.total_rows}")
    print(f"Questions processed: {result.processed_questions}")
    print(f"Answers processed: {result.processed_answers}")
    print(f"Questions created: {result.created_questions}")
    print(f"Questions updated: {result.updated_questions}")
    print(f"Questions skipped: {result.skipped_questions}")

    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        print("-" * 40)
        for error in result.errors:
            row_info = f"Row {error['row_number']}: " if error['row_number'] > 0 else ""
            field_info = f"[{error['field']}] " if error.get('field') else ""
            print(f"  {row_info}{field_info}{error['error_message']}")

    if result.warnings:
        print(f"\nWARNINGS ({len(result.warnings)}):")
        print("-" * 40)
        for warning in result.warnings:
            row_info = f"Row {warning['row_number']}: " if warning['row_number'] > 0 else ""
            field_info = f"[{warning['field']}] " if warning.get('field') else ""
            print(f"  {row_info}{field_info}{warning['error_message']}")

    print("\n" + "="*60)

    # Summary
    if result.errors:
        print("❌ Import completed with errors.")
    elif result.warnings:
        print("⚠️  Import completed with warnings.")
    else:
        print("✅ Import completed successfully!")


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Import questions from XLSX file")
    parser.add_argument("file", help="Path to XLSX file")
    parser.add_argument(
        "--mode",
        choices=["upsert", "replace", "preview"],
        default="upsert",
        help="Import mode (default: upsert)"
    )
    parser.add_argument(
        "--created-by",
        help="UUID of the user creating the questions (optional)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Validate file path
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File '{args.file}' does not exist.")
        sys.exit(1)

    if not file_path.suffix.lower() in ['.xlsx', '.xls']:
        print(f"Error: File '{args.file}' is not an Excel file (.xlsx or .xls).")
        sys.exit(1)

    # Validate created_by if provided
    created_by_id = None
    if args.created_by:
        try:
            from uuid import UUID
            created_by_id = UUID(args.created_by)
        except ValueError:
            print(f"Error: Invalid UUID format for --created-by: {args.created_by}")
            sys.exit(1)

    print(f"Importing from: {file_path}")
    print(f"Mode: {args.mode}")
    if created_by_id:
        print(f"Created by: {created_by_id}")
    print("-" * 40)

    # Import the file
    result = await import_xlsx_file(str(file_path), args.mode, created_by_id)

    # Print results
    print_import_result(result)

    # Exit with appropriate code
    if result.errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())