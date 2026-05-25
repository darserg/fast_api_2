from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Query, status

from src.core.pagination import PaginationParams, get_pagination_params
from src.schemas.common import Page
from src.schemas.posts import (
    PostCreate,
    PostListFilters,
    PostModerationUpdate,
    PostResponse,
    PostUpdate,
)
from src.schemas.users import UserResponse
from src.services.auth import (
    get_current_active_user,
    get_current_active_user_optional,
)
from src.services.posts import PostService

router = APIRouter(prefix="/posts", tags=["posts"], route_class=DishkaRoute)


def get_post_filters(
    search: str | None = Query(default=None),
    author_id: str | None = Query(default=None),
    category_id: str | None = Query(default=None),
    location_id: str | None = Query(default=None),
    is_published: bool | None = Query(default=None),
    moderation_status: str | None = Query(default=None),
    sort_by: str = Query(default="pub_date"),
    sort_order: str = Query(default="desc"),
) -> PostListFilters:
    return PostListFilters(
        search=search,
        author_id=author_id,
        category_id=category_id,
        location_id=location_id,
        is_published=is_published,
        moderation_status=moderation_status,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    post_service: FromDishka[PostService],
    current_user: UserResponse = Depends(get_current_active_user),
):
    return await post_service.create(post, current_user)


@router.get("/", response_model=Page[PostResponse])
async def get_posts(
    post_service: FromDishka[PostService],
    pagination: PaginationParams = Depends(get_pagination_params),
    filters: PostListFilters = Depends(get_post_filters),
):
    return await post_service.list_public(pagination, filters)


@router.get("/admin/moderation/queue", response_model=Page[PostResponse])
async def get_moderation_queue(
    post_service: FromDishka[PostService],
    current_user: UserResponse = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(get_pagination_params),
    filters: PostListFilters = Depends(get_post_filters),
):
    return await post_service.list_for_moderation(pagination, filters, current_user)


@router.post("/admin/moderation/{post_id}", response_model=PostResponse)
async def moderate_post(
    post_id: str,
    payload: PostModerationUpdate,
    post_service: FromDishka[PostService],
    current_user: UserResponse = Depends(get_current_active_user),
):
    return await post_service.moderate(post_id, payload, current_user)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    post_service: FromDishka[PostService],
    current_user: UserResponse | None = Depends(get_current_active_user_optional),
):
    return await post_service.get_visible(post_id, current_user)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    post_update: PostUpdate,
    post_service: FromDishka[PostService],
    current_user: UserResponse = Depends(get_current_active_user),
):
    return await post_service.update(post_id, post_update, current_user)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    post_service: FromDishka[PostService],
    current_user: UserResponse = Depends(get_current_active_user),
):
    await post_service.delete(post_id, current_user)
