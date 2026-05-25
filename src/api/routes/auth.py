from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.core.rate_limit import build_rate_limit_dependency
from src.schemas.auth import RefreshTokenRequest, RegisterRequest, Token
from src.schemas.users import UserResponse
from src.services.auth import AuthService, get_current_active_user

router = APIRouter(prefix="/auth", tags=["authentication"], route_class=DishkaRoute)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(build_rate_limit_dependency("auth.register", 10, 60))],
)
async def register(
    register_data: RegisterRequest,
    auth_service: FromDishka[AuthService],
):
    return await auth_service.register(register_data)


@router.post(
    "/login",
    response_model=Token,
    dependencies=[Depends(build_rate_limit_dependency("auth.login", 20, 60))],
)
async def login(
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: FromDishka[AuthService],
):
    return await auth_service.login(login_data)


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: UserResponse = Depends(get_current_active_user),
):
    return current_user


@router.post(
    "/refresh",
    response_model=Token,
    dependencies=[Depends(build_rate_limit_dependency("auth.refresh", 20, 60))],
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: FromDishka[AuthService],
):
    try:
        return await auth_service.refresh(refresh_data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
