from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from src.schemas.locations import LocationResponse
from src.services.catalog import CatalogService

router = APIRouter(prefix="/locations", tags=["locations"], route_class=DishkaRoute)


@router.get("/", response_model=list[LocationResponse], status_code=status.HTTP_200_OK)
async def get_locations(
    catalog_service: FromDishka[CatalogService],
) -> list[LocationResponse]:
    return list(await catalog_service.list_locations())
