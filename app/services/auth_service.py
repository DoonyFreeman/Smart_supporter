from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories import UserRepository
from app.schemas.auth import TokenResponse
from app.utils.errors import ConflictException, UnauthorizedException
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)

    async def register(
        self, email: str, password: str, full_name: str
    ) -> TokenResponse:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ConflictException("Email already registered")

        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
        )
        user = await self.user_repo.create(user)

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def authenticate(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Incorrect email or password")

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid token type")
            sub = payload.get("sub")
            if sub is None:
                raise UnauthorizedException("Invalid refresh token")
            user_id = int(sub)
        except (ValueError, TypeError):
            raise UnauthorizedException("Invalid refresh token")

        user = await self.user_repo.get(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )
