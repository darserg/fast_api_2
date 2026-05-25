from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.categories import CategoryResponse
from src.schemas.posts import PostListFilters, PostResponse
from src.schemas.common import Page
from src.core.pagination import PaginationParams, get_pagination_params
from src.services.catalog import CatalogService
from src.services.posts import PostService

router = APIRouter(prefix="/categories", tags=["categories"], route_class=DishkaRoute)


@router.get("/", response_model=list[CategoryResponse], status_code=status.HTTP_200_OK)
async def get_categories(
    catalog_service: FromDishka[CatalogService],
) -> list[CategoryResponse]:
    return list(await catalog_service.list_categories())


@router.get("/{slug}/posts", response_model=Page[PostResponse], status_code=status.HTTP_200_OK)
async def get_category_posts(
    slug: str,
    catalog_service: FromDishka[CatalogService],
    post_service: FromDishka[PostService],
    pagination: PaginationParams = Depends(get_pagination_params),
):
    category = await catalog_service.get_category_by_slug(slug)
    if category is None or not category.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    filters = PostListFilters(category_id=category.id)
    return await post_service.list_public(pagination, filters)
