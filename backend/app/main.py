"""Точка входа FastAPI."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __version__
from app.api.public import health
from app.api.router import api_router
from app.core.config import get_settings
from app.core.db import dispose_engine
from app.core.errors import register_error_handlers
from app.core.logging import setup_logging
from app.core.redis import close_redis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info("Запуск API «ДЕТАЛЬ 24» версии %s, режим %s", __version__, settings.app_env)
    yield
    await close_redis()
    await dispose_engine()
    logger.info("API остановлен")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="ДЕТАЛЬ 24 API",
        version=__version__,
        lifespan=lifespan,
        # Интерактивная документация доступна только при разработке
        docs_url="/api/docs" if settings.is_dev else None,
        redoc_url=None,
        openapi_url="/api/openapi.json" if settings.is_dev else None,
    )
    register_error_handlers(app)
    app.include_router(api_router)
    # Короткий адрес /health для мониторинга и скриптов
    app.include_router(health.router)
    return app


app = create_app()
