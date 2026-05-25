from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.posts import Comment, CommentImage, Post
from src.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Comment, session)

    async def get_for_post(self, post_id: str) -> Sequence[Comment]:
        query = (
            self._base_query()
            .where(Comment.post_id == post_id)
            .order_by(Comment.created_at.asc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def refresh_post_comment_count(self, post_id: str) -> None:
        count_query = select(func.count(Comment.id)).where(Comment.post_id == post_id)
        count_result = await self.session.execute(count_query)
        comment_count = count_result.scalar_one()

        post = await self.session.get(Post, post_id)
        if post is not None:
            post.comment_count = comment_count
            self.session.add(post)
            await self.session.flush()

    async def replace_images(self, comment_id: str, images: list[dict]) -> None:
        delete_query = select(CommentImage).where(CommentImage.comment_id == comment_id)
        result = await self.session.execute(delete_query)
        for image in result.scalars().all():
            await self.session.delete(image)

        for position, image in enumerate(images):
            self.session.add(
                CommentImage(
                    comment_id=comment_id,
                    file_key=image["file_key"],
                    file_url=image["file_url"],
                    position=position,
                )
            )
        await self.session.flush()

    async def get_images(self, comment_id: str) -> Sequence[CommentImage]:
        query = (
            select(CommentImage)
            .where(CommentImage.comment_id == comment_id)
            .order_by(CommentImage.position.asc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()
