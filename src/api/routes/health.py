from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request

from src.services.health import HealthService

router = APIRouter(prefix="/health", tags=["health"], route_class=DishkaRoute)


@router.get("/")
async def healthcheck(
    request: Request,
    health_service: FromDishka[HealthService],
):
    payload = await health_service.check()
    payload["request_id"] = getattr(request.state, "request_id", None)
    return payload
