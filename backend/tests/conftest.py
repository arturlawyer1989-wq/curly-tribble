"""Общие фикстуры: тестовая база с настоящими миграциями, отдельная база Redis, HTTP-клиент."""

import os
from collections.abc import AsyncIterator
from pathlib import Path

# Переменные окружения задаются до импорта приложения: настройки читаются один раз
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+asyncpg://detal24:detal24@db:5432/detal24_test"
)
os.environ["REDIS_URL"] = os.environ.get("TEST_REDIS_URL", "redis://redis:6379/1")
os.environ["CELERY_BROKER_URL"] = ""

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import delete  # noqa: E402

from app.core.db import dispose_engine, get_session_factory  # noqa: E402
from app.core.redis import close_redis, get_redis  # noqa: E402
from app.main import app  # noqa: E402
from app.models.shop import ShopSettings  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def migrated_database() -> None:
    """Перед тестами накатываем миграции, после тестов откатываем: проверяется и откат."""
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    yield
    command.downgrade(config, "base")


@pytest.fixture(autouse=True)
async def clean_state() -> AsyncIterator[None]:
    """Каждый тест начинается с пустой таблицы настроек и пустого Redis."""
    async with get_session_factory()() as session:
        await session.execute(delete(ShopSettings))
        await session.commit()
    await get_redis().flushdb()
    yield


@pytest.fixture(scope="session", autouse=True)
async def close_connections() -> AsyncIterator[None]:
    yield
    await close_redis()
    await dispose_engine()


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        yield http
