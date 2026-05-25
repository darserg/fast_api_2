from typing import AsyncIterable

from dishka import Provider, Scope, provide
from dishka.integrations.fastapi import FastapiProvider
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import Database, database
from src.core.storage import StorageService, get_storage_service
from src.repositories.audit import AuditRepository
from src.repositories.categories import CategoryRepository
from src.repositories.comments import CommentRepository
from src.repositories.locations import LocationRepository
from src.repositories.posts import PostRepository
from src.repositories.users import UserRepository
from src.services.audit import AuditService
from src.services.audit_query import AuditQueryService
from src.services.auth import AuthService
from src.services.catalog import CatalogService
from src.services.comments import CommentService
from src.services.health import HealthService
from src.services.media import MediaService
from src.services.posts import PostService
from src.services.users import UserService


class AppProvider(Provider):
    @provide(scope=Scope.APP)
    def get_database(self) -> Database:
        return database

    @provide(scope=Scope.APP)
    def get_storage(self) -> StorageService:
        return get_storage_service()

    @provide(scope=Scope.REQUEST)
    async def get_session(self, db: Database) -> AsyncIterable[AsyncSession]:
        async with db.session() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def get_user_repo(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_post_repo(self, session: AsyncSession) -> PostRepository:
        return PostRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_comment_repo(self, session: AsyncSession) -> CommentRepository:
        return CommentRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_category_repo(self, session: AsyncSession) -> CategoryRepository:
        return CategoryRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_location_repo(self, session: AsyncSession) -> LocationRepository:
        return LocationRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_audit_repo(self, session: AsyncSession) -> AuditRepository:
        return AuditRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_audit_service(
        self,
        audit_repo: AuditRepository,
        request: Request,
    ) -> AuditService:
        return AuditService(audit_repo, request)

    @provide(scope=Scope.REQUEST)
    def get_media_service(self, storage: StorageService) -> MediaService:
        return MediaService(storage)

    @provide(scope=Scope.REQUEST)
    def get_auth_service(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
        audit_service: AuditService,
    ) -> AuthService:
        return AuthService(session, user_repo, audit_service)

    @provide(scope=Scope.REQUEST)
    def get_post_service(
        self,
        post_repo: PostRepository,
        audit_service: AuditService,
        media_service: MediaService,
    ) -> PostService:
        return PostService(post_repo, audit_service, media_service)

    @provide(scope=Scope.REQUEST)
    def get_comment_service(
        self,
        comment_repo: CommentRepository,
        post_repo: PostRepository,
        audit_service: AuditService,
        media_service: MediaService,
    ) -> CommentService:
        return CommentService(comment_repo, post_repo, audit_service, media_service)

    @provide(scope=Scope.REQUEST)
    def get_catalog_service(
        self,
        category_repo: CategoryRepository,
        location_repo: LocationRepository,
    ) -> CatalogService:
        return CatalogService(category_repo, location_repo)

    @provide(scope=Scope.REQUEST)
    def get_user_service(
        self,
        user_repo: UserRepository,
        audit_service: AuditService,
    ) -> UserService:
        return UserService(user_repo, audit_service)

    @provide(scope=Scope.REQUEST)
    def get_health_service(self, session: AsyncSession) -> HealthService:
        return HealthService(session)

    @provide(scope=Scope.REQUEST)
    def get_audit_query_service(self, audit_repo: AuditRepository) -> AuditQueryService:
        return AuditQueryService(audit_repo)


def get_providers() -> tuple[Provider, ...]:
    return (AppProvider(), FastapiProvider())
