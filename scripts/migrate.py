"""Run Alembic migrations with recovery for legacy Docker volumes."""

from __future__ import annotations

import asyncio
import sys

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.config import settings

HEAD_REVISION = "f3a1c9d2b4ef"

# Map existing schema markers to the latest applied Alembic revision.
LEGACY_REVISION_MARKERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (HEAD_REVISION, ("audit_logs",)),
    ("9a6f5a0b7c11", ("comments",)),
    ("be605aea953f", ("posts",)),
    ("21fdbfff93bd", ("users",)),
)


def _alembic_config() -> Config:
    cfg = Config("alembic.ini")
    cfg.set_main_option("script_location", "migrations")
    return cfg


def _detect_legacy_revision(table_names: set[str]) -> str | None:
    for revision, markers in LEGACY_REVISION_MARKERS:
        if any(marker in table_names for marker in markers):
            return revision
    return None


async def _current_state() -> tuple[set[str], str | None]:
    engine = create_async_engine(settings.database_url)

    async with engine.connect() as connection:
        table_names = set(
            await connection.run_sync(
                lambda sync_connection: inspect(sync_connection).get_table_names()
            )
        )
        version: str | None = None
        if "alembic_version" in table_names:
            result = await connection.execute(
                text("SELECT version_num FROM alembic_version LIMIT 1")
            )
            version = result.scalar_one_or_none()

    await engine.dispose()
    return table_names, version


def _stamp_legacy_schema(cfg: Config, table_names: set[str], version: str | None) -> None:
    if version is not None or "users" not in table_names:
        return

    legacy_revision = _detect_legacy_revision(table_names)
    if legacy_revision is None:
        return

    print(
        f"Detected legacy schema without Alembic version; "
        f"stamping {legacy_revision}",
        file=sys.stderr,
    )
    command.stamp(cfg, legacy_revision)


def main() -> None:
    cfg = _alembic_config()
    table_names, version = asyncio.run(_current_state())
    _stamp_legacy_schema(cfg, table_names, version)
    command.upgrade(cfg, "head")


if __name__ == "__main__":
    main()
