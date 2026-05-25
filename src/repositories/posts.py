from datetime import datetime
from typing import Sequence

from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import ModerationStatus, SortOrder
from src.models.posts import Category, Location, Post, PostImage
from src.repositories.base import BaseRepository
from src.schemas.posts import PostListFilters
from src.core.exceptions import PostCreationError, PostNotFound


SORT_FIELDS = {
    "created_at": Post.created_at,
    "updated_at": Post.updated_at,
    "pub_date": Post.pub_date,
    "title": Post.title,
}


class PostRepository(BaseRepository[Post]):
    def __init__(self, session: AsyncSession):
        super().__init__(Post, session)

    async def get_by_author(self, author_id: str) -> Sequence[Post]:
        try:
            query = self._base_query().where(Post.author_id == author_id)
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise PostCreationError(f"Failed to get posts by author: {str(e)}")

    async def get_published(self) -> Sequence[Post]:
        try:
            query = self._public_query()
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise PostCreationError(f"Failed to get published posts: {str(e)}")

    async def get_with_validation(self, post_id: str, include_deleted: bool = False) -> Post:
        post = await self.get(post_id, include_deleted=include_deleted)
        if post is None:
            raise PostNotFound(post_id)
        return post

    async def get_visible(self, post_id: str, viewer_id: str | None = None) -> Post:
        post = await self.get_with_validation(post_id)
        public_query = self._public_query().where(Post.id == post_id)
        public_result = await self.session.execute(public_query)
        if public_result.scalar_one_or_none() is not None:
            return post
        if viewer_id is not None and post.author_id == viewer_id:
            return post
        raise PostNotFound(post_id)

    async def get_public_by_category_slug(self, slug: str) -> Sequence[Post]:
        try:
            query = (
                self._public_query()
                .join(Category, Post.category_id == Category.id)
                .where(Category.slug == slug)
            )
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise PostCreationError(
                f"Failed to get published posts by category: {str(e)}"
            )

    async def get_public_by_author(self, author_id: str) -> Sequence[Post]:
        try:
            query = self._public_query().where(Post.author_id == author_id)
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise PostCreationError(
                f"Failed to get published posts by author: {str(e)}"
            )

    async def list_posts(
        self,
        filters: PostListFilters,
        *,
        include_unpublished: bool = False,
    ) -> Select[tuple[Post]]:
        query = self._base_query().outerjoin(Category, Post.category_id == Category.id)
        query = query.outerjoin(Location, Post.location_id == Location.id)

        if filters.search:
            query = query.where(
                or_(
                    Post.title.ilike(f"%{filters.search}%"),
                    Post.text.ilike(f"%{filters.search}%"),
                )
            )
        if filters.author_id:
            query = query.where(Post.author_id == filters.author_id)
        if filters.category_id:
            query = query.where(Post.category_id == filters.category_id)
        if filters.location_id:
            query = query.where(Post.location_id == filters.location_id)
        if filters.is_published is not None:
            query = query.where(Post.is_published.is_(filters.is_published))
        if filters.moderation_status is not None:
            query = query.where(Post.moderation_status == filters.moderation_status.value)

        if not include_unpublished:
            query = query.where(Post.is_published.is_(True))
            query = query.where(Post.pub_date <= datetime.utcnow())
            query = query.where(or_(Post.category_id.is_(None), Category.is_published.is_(True)))
            query = query.where(or_(Post.location_id.is_(None), Location.is_published.is_(True)))
            query = query.where(
                Post.moderation_status == ModerationStatus.APPROVED.value
            )

        sort_field = SORT_FIELDS.get(filters.sort_by, Post.pub_date)
        query = query.order_by(
            sort_field.asc()
            if filters.sort_order == SortOrder.ASC
            else sort_field.desc()
        )
        return query

    async def replace_images(self, post_id: str, images: list[dict]) -> None:
        delete_query = select(PostImage).where(PostImage.post_id == post_id)
        result = await self.session.execute(delete_query)
        for image in result.scalars().all():
            await self.session.delete(image)

        for position, image in enumerate(images):
            self.session.add(
                PostImage(
                    post_id=post_id,
                    file_key=image["file_key"],
                    file_url=image["file_url"],
                    position=position,
                )
            )
        await self.session.flush()

    async def get_images(self, post_id: str) -> Sequence[PostImage]:
        query = (
            select(PostImage)
            .where(PostImage.post_id == post_id)
            .order_by(PostImage.position.asc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    def _public_query(self) -> Select[tuple[Post]]:
        now = datetime.utcnow()
        return (
            self._base_query()
            .outerjoin(Category, Post.category_id == Category.id)
            .outerjoin(Location, Post.location_id == Location.id)
            .where(Post.is_published.is_(True))
            .where(Post.pub_date <= now)
            .where(or_(Post.category_id.is_(None), Category.is_published.is_(True)))
            .where(or_(Post.location_id.is_(None), Location.is_published.is_(True)))
            .where(Post.moderation_status == ModerationStatus.APPROVED.value)
            .order_by(Post.pub_date.desc())
        )
