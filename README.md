# FastAPI Blogicum API

FastAPI backend with:

- JWT auth with access + refresh tokens
- Dishka-based dependency injection
- Postgres-first configuration with SQLite fallback
- RBAC roles: `author`, `moderator`, `admin`
- Soft delete, moderation and audit logs
- Multiple images for posts and comments
- Healthcheck, structured logging, request-id middleware
- Optional S3/MinIO presigned uploads
- In-memory rate limiting for auth and comments
- Poetry dependency management and test scaffolding

## Quick start

### Docker

```bash
docker compose up --build
```

Что поднимется:

- API: `http://localhost:8000`
- Postgres: `localhost:5433`
- MinIO API: `http://localhost:9000`
- MinIO Console: `http://localhost:9001`

Перед запуском достаточно создать `.env` из [.env.example](C:\fastapi\fast_api_2\.env.example).

### Poetry

```bash
poetry install
poetry run alembic upgrade head
poetry run uvicorn src.main:app --reload
```

## Environment

Use [.env.example](C:\fastapi\fast_api_2\.env.example) as a template.

The app prefers Postgres when `POSTGRES_HOST` or `DATABASE_URL` is set.
If no Postgres settings are provided, it falls back to SQLite.

## Main API areas

- `/auth/*` registration, login, refresh, current user
- `/posts/*` CRUD, public feed, moderation queue
- `/posts/{post_id}/comments/*` CRUD and moderation
- `/categories/*`, `/locations/*`
- `/media/presign` for S3/MinIO upload flow
- `/health/`

## Business-oriented additions already wired

- audit trail table `audit_logs`
- moderation statuses for posts/comments
- role management endpoint for admins
- request correlation through `X-Request-ID`
- optional Sentry/OpenTelemetry bootstrap

## Tests

Test scaffolding lives in `tests/` and is ready for `poetry run pytest` with `httpx`.
