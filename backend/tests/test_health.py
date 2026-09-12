"""Проверка состояния сервисов, включая отказ базы и Redis."""

from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine

from app.api.public import health as health_module
from app.core.config import get_settings
from app.core.redis import get_redis, get_sync_redis
from app.services.heartbeat import HEARTBEAT_KEY, write_heartbeat


async def test_health_without_worker_is_degraded(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["database"]["status"] == "ok"
    assert body["redis"]["status"] == "ok"
    assert body["worker"]["status"] == "unknown"
    assert "воркер" in body["worker"]["message"]
    assert body["version"]


async def test_health_with_fresh_heartbeat_is_ok(client: AsyncClient) -> None:
    sync_client = get_sync_redis()
    try:
        write_heartbeat(sync_client, ttl_seconds=get_settings().worker_heartbeat_stale_after_seconds)
    finally:
        sync_client.close()
    body = (await client.get("/api/v1/health")).json()
    assert body["status"] == "ok"
    assert body["worker"]["status"] == "ok"


async def test_health_with_old_heartbeat_is_stale(client: AsyncClient) -> None:
    old = datetime.now(UTC) - timedelta(seconds=get_settings().worker_heartbeat_stale_after_seconds + 60)
    await get_redis().set(HEARTBEAT_KEY, old.isoformat())
    body = (await client.get("/api/v1/health")).json()
    assert body["status"] == "degraded"
    assert body["worker"]["status"] == "stale"


async def test_health_reports_redis_failure(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    import redis.asyncio as redis_async

    broken = redis_async.from_url("redis://127.0.0.1:1/0", socket_connect_timeout=0.5, socket_timeout=0.5)
    monkeypatch.setattr(health_module, "get_redis", lambda: broken)
    response = await client.get("/api/v1/health")
    await broken.aclose()
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "error"
    assert body["redis"]["status"] == "error"
    assert body["redis"]["message"] == "Redis недоступен."
    assert body["worker"]["status"] == "unknown"


async def test_health_reports_database_failure(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    broken = create_async_engine("postgresql+asyncpg://nobody:nothing@127.0.0.1:1/nowhere")
    monkeypatch.setattr(health_module, "get_engine", lambda: broken)
    response = await client.get("/api/v1/health")
    await broken.dispose()
    assert response.status_code == 503
    body = response.json()
    assert body["database"]["status"] == "error"
    assert body["database"]["message"] == "База данных недоступна."
