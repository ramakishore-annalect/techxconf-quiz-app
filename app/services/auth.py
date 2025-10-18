"""Authentication service."""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.models import User, UserRole
from app.schemas.auth import UserRegister, UserLogin
from app.utils.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)


class AuthService:
    """Authentication service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_data: UserRegister) -> User:
        """Register a new user."""
        # Check if user already exists
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValueError("Email already registered")

        # Create new user
        user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            display_name=user_data.display_name or user_data.email.split("@")[0],
            role=UserRole.USER,
            is_active=True,
            is_verified=False,  # Email verification can be added later
        )

        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Email already registered")

    async def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """Authenticate a user."""
        # Get user by email
        result = await self.db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(login_data.password, user.password_hash):
            return None

        if not user.is_active:
            return None

        return user

    async def create_user_tokens(self, user: User) -> Tuple[str, str]:
        """Create access and refresh tokens for user."""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        access_token = create_access_token(
            subject=str(user.id),
            expires_delta=access_token_expires
        )

        refresh_token = create_refresh_token(
            subject=str(user.id),
            expires_delta=refresh_token_expires
        )

        return access_token, refresh_token

    async def refresh_user_token(self, refresh_token: str) -> Optional[Tuple[str, str]]:
        """Refresh user tokens."""
        user_id = verify_refresh_token(refresh_token)
        if not user_id:
            return None

        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return None

        # Get user from database
        result = await self.db.execute(select(User).where(User.id == user_uuid))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            return None

        return await self.create_user_tokens(user)

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def update_user(self, user_id: UUID, **updates) -> Optional[User]:
        """Update user information."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return None

        for field, value in updates.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)

        user.updated_at = datetime.utcnow()

        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            await self.db.rollback()
            return None

    async def change_password(
        self, user_id: UUID, current_password: str, new_password: str
    ) -> bool:
        """Change user password."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return False

        if not verify_password(current_password, user.password_hash):
            return False

        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()

        await self.db.commit()
        return True

    async def reset_password(self, email: str, new_password: str) -> bool:
        """Reset user password."""
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return False

        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()

        await self.db.commit()
        return True

    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate a user."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return False

        user.is_active = False
        user.updated_at = datetime.utcnow()

        await self.db.commit()
        return True

    async def activate_user(self, user_id: UUID) -> bool:
        """Activate a user."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return False

        user.is_active = True
        user.updated_at = datetime.utcnow()

        await self.db.commit()
        return True