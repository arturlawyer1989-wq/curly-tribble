"""Первичное заполнение базы. Запуск: python -m app.seeds.apply. Повторный запуск ничего не ломает."""

import asyncio
import logging

from app.core.config import get_settings
from app.core.db import dispose_engine, get_session_factory
from app.core.logging import setup_logging
from app.services.shop import ensure_shop

logger = logging.getLogger("app.seeds")


async def apply_seeds() -> None:
    settings = get_settings()
    async with get_session_factory()() as session:
        shop, created = await ensure_shop(session, settings)
    if created:
        logger.info("Созданы настройки магазина «%s»", shop.name)
    else:
        logger.info("Настройки магазина уже есть («%s»), ничего не меняем", shop.name)


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    asyncio.run(_run())


async def _run() -> None:
    try:
        await apply_seeds()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    main()
