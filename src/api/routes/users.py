from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.common import Page
from src.schemas.posts import PostListFilters, PostResponse
from src.schemas.users import UserResponse, UserRoleUpdate, UserUpdate
from src.services.auth import (
    get_current_active_user,
    get_current_active_user_optional,
)
from src.services.posts import PostService
from src.services.users import UserService
from src.core.pagination import PaginationParams, get_pagination_params

router = APIRouter(prefix="/users", tags=["users"], route_class=DishkaRoute)


@router.get("/", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(
    user_service: FromDishka[UserService],
    current_user: UserResponse = Depends(get_current_active_user),
) -> list[UserResponse]:
    user_service.require_staff(current_user)
    return list(await user_service.list_users())


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: str,
    user_service: FromDishka[UserService],
    current_user: UserResponse = Depends(get_current_active_user),
):
    if current_user.id != user_id and current_user.role not in {"moderator", "admin"}:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await user_service.get_user(user_id)


@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    user_service: FromDishka[UserService],
    current_user: UserResponse = Depends(get_current_active_user),
):
    return await user_service.update_user(user_id, user_update, current_user)


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_role(
    user_id: str,
    payload: UserRoleUpdate,
    user_service: FromDishka[UserService],
    current_user: UserResponse = Depends(get_current_active_user),
):
    return await user_service.update_role(user_id, payload, current_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    user_service: FromDishka[UserService],
    current_user: UserResponse = Depends(get_current_active_user),
):
    await user_service.delete_user(user_id, current_user)


@router.get("/profile/{username}", response_model=Page[PostResponse], status_code=status.HTTP_200_OK)
async def get_user_posts(
    username: str,
    user_service: FromDishka[UserService],
    post_service: FromDishka[PostService],
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: UserResponse | None = Depends(get_current_active_user_optional),
):
    user = await user_service.get_by_username(username)
    filters = PostListFilters(author_id=user.id)
    return await post_service.list_for_profile(
        pagination,
        filters,
        current_user,
        owner_id=user.id,
    )
