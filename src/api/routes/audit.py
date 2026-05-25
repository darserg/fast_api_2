from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends

from src.core.pagination import PaginationParams, get_pagination_params
from src.schemas.audit import AuditLogResponse
from src.schemas.common import Page
from src.schemas.users import UserResponse
from src.services.audit_query import AuditQueryService
from src.services.auth import get_current_active_user

router = APIRouter(prefix="/audit", tags=["audit"], route_class=DishkaRoute)


@router.get("/", response_model=Page[AuditLogResponse])
async def get_audit_logs(
    audit_service: FromDishka[AuditQueryService],
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: UserResponse = Depends(get_current_active_user),
):
    return await audit_service.list_logs(pagination, current_user)
