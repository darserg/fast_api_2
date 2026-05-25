from fastapi import HTTPException, status

from src.core.enums import ModerationStatus, UserRole
from src.core.pagination import PaginationParams
from src.repositories.posts import PostRepository
from src.schemas.common import Page
from src.schemas.posts import (
    PostCreate,
    PostListFilters,
    PostModerationUpdate,
    PostResponse,
    PostUpdate,
)
from src.schemas.users import UserResponse
from src.services.audit import AuditService
from src.services.media import MediaService


class PostService:
    def __init__(
        self,
        post_repo: PostRepository,
        audit_service: AuditService,
        media_service: MediaService,
    ) -> None:
        self.post_repo = post_repo
        self.audit_service = audit_service
        self.media_service = media_service

    async def list_public(
        self,
        pagination: PaginationParams,
        filters: PostListFilters,
    ) -> Page[PostResponse]:
        query = await self.post_repo.list_posts(filters, include_unpublished=False)
        items, total = await self.post_repo.get_page(pagination, query)
        return await self._build_page(items, pagination, total)

    async def list_for_moderation(
        self,
        pagination: PaginationParams,
        filters: PostListFilters,
        current_user: UserResponse,
    ) -> Page[PostResponse]:
        self._require_staff(current_user)
        query = await self.post_repo.list_posts(filters, include_unpublished=True)
        items, total = await self.post_repo.get_page(pagination, query)
        return await self._build_page(items, pagination, total)

    async def list_for_profile(
        self,
        pagination: PaginationParams,
        filters: PostListFilters,
        current_user: UserResponse | None,
        owner_id: str,
    ) -> Page[PostResponse]:
        if current_user is not None and (
            current_user.id == owner_id
            or current_user.role in {UserRole.MODERATOR, UserRole.ADMIN}
        ):
            query = await self.post_repo.list_posts(filters, include_unpublished=True)
            items, total = await self.post_repo.get_page(pagination, query)
            return await self._build_page(items, pagination, total)
        return await self.list_public(pagination, filters)

    async def get_visible(self, post_id: str, current_user: UserResponse | None):
        viewer_id = current_user.id if current_user is not None else None
        post = await self.post_repo.get_visible(post_id, viewer_id)
        return await self._attach_images(post)

    async def create(self, payload: PostCreate, current_user: UserResponse):
        post_data = payload.model_dump(exclude={"image_keys", "author_id"})
        post_data["author_id"] = current_user.id
        post_data["moderation_status"] = ModerationStatus.PENDING.value
        created = await self.post_repo.create(post_data)
        await self.post_repo.replace_images(
            created.id,
            self.media_service.build_image_payloads(payload.image_keys),
        )
        await self.audit_service.log(
            actor_id=current_user.id,
            action="post.create",
            entity_type="post",
            entity_id=created.id,
            after_state=post_data,
        )
        return await self._attach_images(created)

    async def update(
        self,
        post_id: str,
        payload: PostUpdate,
        current_user: UserResponse,
    ):
        post = await self.post_repo.get_with_validation(post_id)
        self._require_owner_or_staff(post.author_id, current_user)
        before_state = {
            "title": post.title,
            "text": post.text,
            "pub_date": post.pub_date.isoformat(),
            "is_published": post.is_published,
        }
        update_data = payload.model_dump(exclude_unset=True, exclude={"image_keys"})
        if update_data:
            update_data["moderation_status"] = ModerationStatus.PENDING.value
            post = await self.post_repo.update(post, update_data)
        if payload.image_keys is not None:
            await self.post_repo.replace_images(
                post.id,
                self.media_service.build_image_payloads(payload.image_keys),
            )
        await self.audit_service.log(
            actor_id=current_user.id,
            action="post.update",
            entity_type="post",
            entity_id=post.id,
            before_state=before_state,
            after_state=update_data or None,
        )
        return await self._attach_images(post)

    async def moderate(
        self,
        post_id: str,
        payload: PostModerationUpdate,
        current_user: UserResponse,
    ):
        self._require_staff(current_user)
        post = await self.post_repo.get_with_validation(post_id)
        before_state = {
            "moderation_status": post.moderation_status,
            "moderation_reason": post.moderation_reason,
        }
        post = await self.post_repo.update(
            post,
            {
                "moderation_status": payload.moderation_status.value,
                "moderation_reason": payload.moderation_reason,
                "moderated_by_id": current_user.id,
            },
        )
        await self.audit_service.log(
            actor_id=current_user.id,
            action="post.moderate",
            entity_type="post",
            entity_id=post.id,
            before_state=before_state,
            after_state=payload.model_dump(),
        )
        return await self._attach_images(post)

    async def delete(self, post_id: str, current_user: UserResponse) -> None:
        post = await self.post_repo.get_with_validation(post_id)
        self._require_owner_or_staff(post.author_id, current_user)
        await self.post_repo.delete(post)
        await self.audit_service.log(
            actor_id=current_user.id,
            action="post.delete",
            entity_type="post",
            entity_id=post.id,
        )

    async def _build_page(
        self,
        items,
        pagination: PaginationParams,
        total: int,
    ) -> Page[PostResponse]:
        resolved = [await self._attach_images(item) for item in items]
        return Page(
            items=resolved,
            page=pagination.page,
            size=pagination.size,
            total=total,
        )

    async def _attach_images(self, post):
        post.images = list(await self.post_repo.get_images(post.id))
        return post

    @staticmethod
    def _require_owner_or_staff(owner_id: str, current_user: UserResponse) -> None:
        if owner_id == current_user.id:
            return
        if current_user.role in {UserRole.MODERATOR, UserRole.ADMIN}:
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    @staticmethod
    def _require_staff(current_user: UserResponse) -> None:
        if current_user.role not in {UserRole.MODERATOR, UserRole.ADMIN}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff permissions required",
            )
