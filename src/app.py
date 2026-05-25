from contextlib import asynccontextmanager

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api.routes.audit import router as audit_router
from src.api.routes.categories import router as categories_router
from src.api.routes.comments import router as comments_router
from src.api.routes.health import router as health_router
from src.api.routes.locations import router as locations_router
from src.api.routes.media import router as media_router
from src.api.routes.posts import router as posts_router
from src.api.routes.auth import router as auth_router
from src.api.routes.users import router as users_router
from src.core.db import database
from src.core.logging import setup_logging
from src.core.middleware import RequestContextMiddleware
from src.core.observability import setup_observability
from src.core.rate_limit import InMemoryRateLimiter
from src.di.providers import get_providers


def create_app() -> FastAPI:
    setup_logging()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        await app.state.dishka_container.close()

    app = FastAPI(
        title="FastAPI Blogicum API",
        version="0.2.0",
        lifespan=lifespan,
    )
    app.state.database = database
    app.state.rate_limiter = InMemoryRateLimiter()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(posts_router)
    app.include_router(categories_router)
    app.include_router(locations_router)
    app.include_router(comments_router)
    app.include_router(media_router)
    app.include_router(health_router)
    app.include_router(audit_router)

    container = make_async_container(*get_providers())
    setup_dishka(container=container, app=app)
    setup_observability(app)

    return app
