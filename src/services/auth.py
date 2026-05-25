from datetime import datetime, timedelta

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.enums import UserRole
from src.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_token,
)
from src.repositories.users import UserRepository
from src.schemas.auth import LoginRequest, RefreshTokenRequest, RegisterRequest
from src.schemas.users import UserCreate, UserResponse
from src.core.exceptions import UserAlreadyExists, AuthenticationError
from src.services.audit import AuditService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


class AuthService:
    def __init__(
        self,
        db: AsyncSession,
        user_repo: UserRepository,
        audit_service: AuditService,
    ) -> None:
        self.db = db
        self.user_repo = user_repo
        self.audit_service = audit_service

    async def authenticate_user(self, username: str, password: str) -> UserResponse | None:
        user = await self.user_repo.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def login(self, login_data: LoginRequest) -> dict:
        user = await self.authenticate_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=access_token_expires,
        )
        refresh_token = create_refresh_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        user.last_login_at = datetime.utcnow()
        await self.db.flush()
        await self.audit_service.log(
            actor_id=user.id,
            action="auth.login",
            entity_type="user",
            entity_id=user.id,
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def register(self, register_data: RegisterRequest) -> UserResponse:
        existing_user = await self.user_repo.get_by_username(register_data.username)
        if existing_user:
            raise UserAlreadyExists(register_data.username)

        existing_email = await self.user_repo.get_by_email(register_data.email)
        if existing_email:
            raise UserAlreadyExists(register_data.email)

        user_create = UserCreate(
            first_name=register_data.first_name,
            last_name=register_data.last_name,
            username=register_data.username,
            email=register_data.email,
            password=register_data.password,
        )
        user_data = user_create.model_dump()
        if "password" in user_data and hasattr(user_data["password"], "get_secret_value"):
            user_data["password"] = user_data["password"].get_secret_value()
        user_data["role"] = UserRole.AUTHOR.value
        created_user = await self.user_repo.create(user_data)
        await self.audit_service.log(
            actor_id=created_user.id,
            action="auth.register",
            entity_type="user",
            entity_id=created_user.id,
        )
        return created_user

    async def refresh(self, refresh_data: RefreshTokenRequest) -> dict:
        username = verify_token(refresh_data.refresh_token, expected_type="refresh")
        if username is None:
            raise AuthenticationError(detail="Could not validate refresh token")

        user = await self.user_repo.get_by_username(username)
        if user is None or not user.is_active:
            raise AuthenticationError(detail="Could not validate refresh token")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=access_token_expires,
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def resolve_user_from_token(self, token: str) -> UserResponse:
        username = verify_token(token, expected_type="access")
        if username is None:
            raise AuthenticationError(detail="Could not validate credentials")
        user = await self.user_repo.get_by_username(username)
        if user is None:
            raise AuthenticationError(detail="Could not validate credentials")
        return user


@inject
async def get_current_user(
    auth_service: FromDishka[AuthService],
    token: str = Depends(oauth2_scheme),
) -> UserResponse:
    return await auth_service.resolve_user_from_token(token)


@inject
async def get_current_user_optional(
    auth_service: FromDishka[AuthService],
    token: str | None = Depends(oauth2_scheme_optional),
) -> UserResponse | None:
    if not token:
        return None
    try:
        return await auth_service.resolve_user_from_token(token)
    except AuthenticationError:
        return None


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


async def get_current_active_user_optional(
    current_user: UserResponse | None = Depends(get_current_user_optional),
) -> UserResponse | None:
    if current_user is None or not current_user.is_active:
        return None
    return current_user
