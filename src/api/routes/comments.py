from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Query, status

from src.core.pagination import PaginationParams, get_pagination_params
from src.core.rate_limit import build_rate_limit_dependency
from src.schemas.comments import (
    CommentCreate,
    CommentListFilters,
    CommentModerationUpdate,
    CommentResponse,
    CommentUpdate,
)
from src.schemas.common import Page
from src.schemas.users import UserResponse
from src.services.auth import (
    get_current_active_user,
    get_current_active_user_optional,
)
from src.services.comments import CommentService

router = APIRouter(
    prefix="/posts/{post_id}/comments",
    tags=["comments"],
    route_class=DishkaRoute,
)


def get_comment_filters(
    moderation_status: str | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="asc"),
) -> CommentListFilters:
    return CommentListFilters(
        moderation_status=moderation_status,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/", response_model=Page[CommentResponse])
async def get_comments(
    post_id: str,
    comment_service: FromDishka[CommentService],
    pagination: PaginationParams = Depends(get_pagination_params),
    filters: CommentListFilters = Depends(get_comment_filters),
    current_user: UserResponse | None = Depends(get_current_active_user_optional),
):
    return await comment_service.list_for_post(post_id, pagination, filters, current_user)


@router.post(
    "/",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(build_rate_limit_dependency("comment.create", 30, 60))],
)
async def create_comment(
    post_id: str,
    comment: CommentCreate,
    comment_service: FromDishka[CommentService],
    current_user: UserResponse = Depends(get_current_active_user),
):
    return await comment_service.create(post_id, comment, current_user)


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    post_id: str,
    comment_id: str,
    payload: CommentUpdate,
    comment_service: FromDishka[CommentService],
    current_user: UserResponse = Depends(get_current_active_user),
):
    return await comment_service.update(post_id, comment_id, payload, current_user)


@router.post("/{comment_id}/moderate", response_model=CommentResponse)
async def moderate_comment(
    post_id: str,
    comment_id: str,
    payload: CommentModerationUpdate,
    comment_service: FromDishka[CommentService],
    current_user: UserResponse = Depends(get_current_active_user),
):
    return await comment_service.moderate(post_id, comment_id, payload, current_user)


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(build_rate_limit_dependency("comment.delete", 20, 60))],
)
async def delete_comment(
    post_id: str,
    comment_id: str,
    comment_service: FromDishka[CommentService],
    current_user: UserResponse = Depends(get_current_active_user),
):
    await comment_service.delete(post_id, comment_id, current_user)
