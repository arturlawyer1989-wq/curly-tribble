"""Общие фикстуры: тестовая база с настоящими миграциями, отдельная база Redis, HTTP-клиент, сотрудники."""

import os
from collections.abc import AsyncIterator
from pathlib import Path

# Переменные окружения задаются до импорта приложения: настройки читаются один раз
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", "postgresql+asyncpg://detal24:detal24@db:5432/detal24_test")
os.environ["REDIS_URL"] = os.environ.get("TEST_REDIS_URL", "redis://redis:6379/1")
os.environ["CELERY_BROKER_URL"] = ""
os.environ["SECRET_KEY"] = "test-secret-key-0123456789-abcdefghij-0123456789"
os.environ["ADMIN_LOGIN"] = ""
os.environ["ADMIN_PASSWORD"] = ""

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.db import Base, dispose_engine, get_engine, get_session_factory  # noqa: E402
from app.core.redis import close_redis, get_redis  # noqa: E402
from app.main import app  # noqa: E402
from app.models.admin import AdminUser  # noqa: E402
from app.models.orders import ORDER_NUMBER_SEQUENCE, ORDER_NUMBER_START  # noqa: E402
from app.services.admin_auth import create_admin_user  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parents[1]

OWNER_PASSWORD = "Owner-Pass-123"
MANAGER_PASSWORD = "Manager-Pass-123"


def alembic_config() -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return config


@pytest.fixture(scope="session", autouse=True)
def migrated_database() -> None:
    """Перед тестами накатываем миграции, после тестов откатываем: проверяется и откат."""
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    _quiet_test_database_log()
    yield
    command.downgrade(config, "base")


def _quiet_test_database_log() -> None:
    """Тесты намеренно нарушают ограничения базы; чтобы PostgreSQL не писал эти ожидаемые ошибки
    в общий лог контейнера, для тестовой базы поднимаем порог логирования. Нужны права суперпользователя,
    поэтому при их отсутствии (например, на локальной машине) шаг просто пропускается."""
    from sqlalchemy import create_engine

    from app.core.config import get_settings

    engine = create_engine(get_settings().sync_database_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as conn:
            db_name = conn.execute(text("SELECT current_database()")).scalar()
            conn.execute(text(f'ALTER DATABASE "{db_name}" SET log_min_messages = fatal'))
    except Exception:  # noqa: BLE001 - нет прав: ошибки ограничений просто попадут в лог сервера
        pass
    finally:
        engine.dispose()


@pytest.fixture(autouse=True)
async def clean_state() -> AsyncIterator[None]:
    """Каждый тест начинается с пустых таблиц, пустого Redis и номера заказа 2401."""
    tables = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
    async with get_engine().begin() as conn:
        await conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
        await conn.execute(text(f"ALTER SEQUENCE {ORDER_NUMBER_SEQUENCE} RESTART WITH {ORDER_NUMBER_START}"))
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


@pytest.fixture
async def owner() -> AdminUser:
    async with get_session_factory()() as session:
        user = await create_admin_user(session, login="owner", password=OWNER_PASSWORD, full_name="Артур", role="owner")
        await session.commit()
        await session.refresh(user)
        return user


@pytest.fixture
async def manager() -> AdminUser:
    async with get_session_factory()() as session:
        user = await create_admin_user(session, login="manager", password=MANAGER_PASSWORD, full_name="Менеджер", role="manager")
        await session.commit()
        await session.refresh(user)
        return user
