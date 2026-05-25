from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends

from src.schemas.media import PresignUploadRequest, PresignUploadResponse
from src.schemas.users import UserResponse
from src.services.auth import get_current_active_user
from src.services.media import MediaService

router = APIRouter(prefix="/media", tags=["media"], route_class=DishkaRoute)


@router.post("/presign", response_model=PresignUploadResponse)
async def create_presigned_upload(
    payload: PresignUploadRequest,
    media_service: FromDishka[MediaService],
    current_user: UserResponse = Depends(get_current_active_user),
):
    presigned = media_service.create_presigned_upload(
        object_name=payload.object_name,
        content_type=payload.content_type,
        folder=payload.folder,
    )
    return PresignUploadResponse(
        key=presigned.key,
        upload_url=presigned.upload_url,
        public_url=presigned.public_url,
    )
