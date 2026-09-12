"""Миграции обратимы: откат до нуля и повторный накат, модели совпадают с базой."""

from alembic import command
from alembic.script import ScriptDirectory

from app.core.db import get_session_factory
from sqlalchemy import text
from tests.conftest import alembic_config


async def test_downgrade_and_upgrade_again_leave_full_schema() -> None:
    config = alembic_config()
    command.downgrade(config, "base")
    async with get_session_factory()() as session:
        after_downgrade = await session.scalar(text("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'"))
    command.upgrade(config, "head")
    async with get_session_factory()() as session:
        after_upgrade = await session.scalar(text("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'"))
        version = await session.scalar(text("SELECT version_num FROM alembic_version"))
    heads = ScriptDirectory.from_config(config).get_heads()
    assert after_downgrade == 1  # осталась только служебная таблица alembic_version
    assert after_upgrade == 33
    assert [version] == heads


def test_models_match_migrations() -> None:
    """alembic check падает, если модели разошлись с миграциями."""
    command.check(alembic_config())
