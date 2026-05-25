from fastapi import HTTPException, status

from src.core.enums import ModerationStatus, SortOrder, UserRole
from src.core.pagination import PaginationParams
from src.repositories.comments import CommentRepository
from src.repositories.posts import PostRepository
from src.schemas.comments import (
    CommentCreate,
    CommentListFilters,
    CommentModerationUpdate,
    CommentResponse,
    CommentUpdate,
)
from src.schemas.common import Page
from src.schemas.users import UserResponse
from src.services.audit import AuditService
from src.services.media import MediaService


class CommentService:
    def __init__(
        self,
        comment_repo: CommentRepository,
        post_repo: PostRepository,
        audit_service: AuditService,
        media_service: MediaService,
    ) -> None:
        self.comment_repo = comment_repo
        self.post_repo = post_repo
        self.audit_service = audit_service
        self.media_service = media_service

    async def list_for_post(
        self,
        post_id: str,
        pagination: PaginationParams,
        filters: CommentListFilters,
        current_user: UserResponse | None,
    ) -> Page[CommentResponse]:
        viewer_id = current_user.id if current_user is not None else None
        await self.post_repo.get_visible(post_id, viewer_id=viewer_id)
        items = list(await self.comment_repo.get_for_post(post_id))
        if filters.moderation_status is not None:
            items = [
                item
                for item in items
                if item.moderation_status == filters.moderation_status.value
            ]
        else:
            items = [
                item
                for item in items
                if item.moderation_status == ModerationStatus.APPROVED.value
                or (
                    current_user is not None
                    and item.author_id == current_user.id
                )
            ]
        items.sort(
            key=lambda item: item.created_at,
            reverse=filters.sort_order == SortOrder.DESC,
        )
        total = len(items)
        paged = items[pagination.offset : pagination.offset + pagination.size]
        resolved = [await self._attach_images(item) for item in paged]
        return Page(
            items=resolved,
            page=pagination.page,
            size=pagination.size,
            total=total,
        )

    async def create(self, post_id: str, payload: CommentCreate, current_user: UserResponse):
        await self.post_repo.get_visible(post_id, viewer_id=current_user.id)
        created = await self.comment_repo.create(
            {
                "post_id": post_id,
                "author_id": current_user.id,
                "text": payload.text,
                "moderation_status": ModerationStatus.PENDING.value,
            }
        )
        await self.comment_repo.replace_images(
            created.id,
            self.media_service.build_image_payloads(payload.image_keys),
        )
        await self.comment_repo.refresh_post_comment_count(post_id)
        await self.audit_service.log(
            actor_id=current_user.id,
            action="comment.create",
            entity_type="comment",
            entity_id=created.id,
            after_state={"text": payload.text},
        )
        return await self._attach_images(created)

    async def update(
        self,
        post_id: str,
        comment_id: str,
        payload: CommentUpdate,
        current_user: UserResponse,
    ):
        comment = await self.comment_repo.get(comment_id)
        if comment is None or comment.post_id != post_id:
            raise HTTPException(status_code=404, detail="Comment not found")
        self._require_owner_or_staff(comment.author_id, current_user)
        update_data = payload.model_dump(exclude_unset=True, exclude={"image_keys"})
        if update_data:
            update_data["moderation_status"] = ModerationStatus.PENDING.value
            comment = await self.comment_repo.update(comment, update_data)
        if payload.image_keys is not None:
            await self.comment_repo.replace_images(
                comment.id,
                self.media_service.build_image_payloads(payload.image_keys),
            )
        await self.audit_service.log(
            actor_id=current_user.id,
            action="comment.update",
            entity_type="comment",
            entity_id=comment.id,
            after_state=update_data or None,
        )
        return await self._attach_images(comment)

    async def moderate(
        self,
        post_id: str,
        comment_id: str,
        payload: CommentModerationUpdate,
        current_user: UserResponse,
    ):
        self._require_staff(current_user)
        comment = await self.comment_repo.get(comment_id)
        if comment is None or comment.post_id != post_id:
            raise HTTPException(status_code=404, detail="Comment not found")
        comment = await self.comment_repo.update(
            comment,
            payload.model_dump(),
        )
        await self.audit_service.log(
            actor_id=current_user.id,
            action="comment.moderate",
            entity_type="comment",
            entity_id=comment.id,
            after_state=payload.model_dump(),
        )
        return await self._attach_images(comment)

    async def delete(self, post_id: str, comment_id: str, current_user: UserResponse) -> None:
        comment = await self.comment_repo.get(comment_id)
        if comment is None or comment.post_id != post_id:
            raise HTTPException(status_code=404, detail="Comment not found")
        self._require_owner_or_staff(comment.author_id, current_user)
        await self.comment_repo.delete(comment)
        await self.comment_repo.refresh_post_comment_count(post_id)
        await self.audit_service.log(
            actor_id=current_user.id,
            action="comment.delete",
            entity_type="comment",
            entity_id=comment.id,
        )

    async def _attach_images(self, comment):
        comment.images = list(await self.comment_repo.get_images(comment.id))
        return comment

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
