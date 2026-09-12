"""Фоновая задача heartbeat и её отражение в состоянии."""

from app.core.config import get_settings
from app.core.redis import get_redis
from app.services.heartbeat import HEARTBEAT_KEY, worker_status
from app.workers.tasks import heartbeat


async def test_heartbeat_task_writes_key_with_ttl() -> None:
    stamp = heartbeat.apply().get()
    client = get_redis()
    assert await client.get(HEARTBEAT_KEY) == stamp
    ttl = await client.ttl(HEARTBEAT_KEY)
    assert 0 < ttl <= get_settings().worker_heartbeat_stale_after_seconds
    status = await worker_status(client, get_settings().worker_heartbeat_stale_after_seconds)
    assert status.status == "ok"


async def test_worker_status_handles_corrupted_value() -> None:
    client = get_redis()
    await client.set(HEARTBEAT_KEY, "не дата")
    status = await worker_status(client, 60)
    assert status.status == "error"
