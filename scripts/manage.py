#!/usr/bin/env python3
"""Database management script."""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from alembic import command
from alembic.config import Config
from app.core.config import settings
from app.core.database import engine
from app.models import Base, User, UserRole
from app.utils.security import hash_password


async def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully!")


async def drop_tables():
    """Drop all database tables."""
    print("Dropping database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("Tables dropped successfully!")


async def create_admin_user(email: str = None, password: str = None):
    """Create an admin user."""
    email = email or settings.FIRST_ADMIN_EMAIL
    password = password or settings.FIRST_ADMIN_PASSWORD

    print(f"Creating admin user: {email}")

    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        # Check if admin user already exists
        result = await session.execute(
            "SELECT id FROM users WHERE email = :email",
            {"email": email}
        )
        if result.fetchone():
            print(f"Admin user {email} already exists!")
            return

        # Create admin user
        admin_user = User(
            email=email,
            password_hash=hash_password(password),
            display_name="Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        )

        session.add(admin_user)
        await session.commit()
        print(f"Admin user {email} created successfully!")


def run_alembic_command(command_name: str, *args):
    """Run an Alembic command."""
    alembic_cfg = Config("alembic.ini")
    if command_name == "revision":
        command.revision(alembic_cfg, *args, autogenerate=True)
    elif command_name == "upgrade":
        command.upgrade(alembic_cfg, args[0] if args else "head")
    elif command_name == "downgrade":
        command.downgrade(alembic_cfg, args[0] if args else "-1")
    elif command_name == "history":
        command.history(alembic_cfg)
    elif command_name == "current":
        command.current(alembic_cfg)
    else:
        print(f"Unknown alembic command: {command_name}")


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Database management script")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Database commands
    subparsers.add_parser("create-tables", help="Create all database tables")
    subparsers.add_parser("drop-tables", help="Drop all database tables")

    # Admin user command
    admin_parser = subparsers.add_parser("create-admin", help="Create admin user")
    admin_parser.add_argument("--email", help="Admin email")
    admin_parser.add_argument("--password", help="Admin password")

    # Alembic commands
    revision_parser = subparsers.add_parser("revision", help="Create new migration")
    revision_parser.add_argument("-m", "--message", required=True, help="Migration message")

    upgrade_parser = subparsers.add_parser("upgrade", help="Run migrations")
    upgrade_parser.add_argument("revision", nargs="?", default="head", help="Target revision")

    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade migrations")
    downgrade_parser.add_argument("revision", nargs="?", default="-1", help="Target revision")

    subparsers.add_parser("history", help="Show migration history")
    subparsers.add_parser("current", help="Show current migration")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "create-tables":
            await create_tables()
        elif args.command == "drop-tables":
            await drop_tables()
        elif args.command == "create-admin":
            await create_admin_user(args.email, args.password)
        elif args.command == "revision":
            run_alembic_command("revision", message=args.message)
        elif args.command == "upgrade":
            run_alembic_command("upgrade", args.revision)
        elif args.command == "downgrade":
            run_alembic_command("downgrade", args.revision)
        elif args.command == "history":
            run_alembic_command("history")
        elif args.command == "current":
            run_alembic_command("current")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # Close database connection
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())