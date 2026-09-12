"""Подключение к Redis (асинхронный клиент для API, синхронный для фоновых задач)."""

import redis as redis_sync
import redis.asyncio as redis_async

from app.core.config import get_settings

_client: redis_async.Redis | None = None


def get_redis() -> redis_async.Redis:
    """Общий клиент на всё приложение; соединения берутся из пула."""
    global _client
    if _client is None:
        _client = redis_async.from_url(
            get_settings().redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
    return _client


def get_sync_redis() -> redis_sync.Redis:
    """Синхронный клиент для Celery-задач: там нет цикла событий."""
    return redis_sync.from_url(
        get_settings().redis_url,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )


async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
    _client = None
