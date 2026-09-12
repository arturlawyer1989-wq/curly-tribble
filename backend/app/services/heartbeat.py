"""Отметка «фоновый воркер жив» в Redis и её проверка."""

from datetime import UTC, datetime

import redis as redis_sync
import redis.asyncio as redis_async

from app.schemas.health import ComponentStatus

HEARTBEAT_KEY = "d24:worker:heartbeat"


def write_heartbeat(client: redis_sync.Redis, ttl_seconds: int) -> str:
    """Записать текущее время; ключ сам исчезнет, если воркер перестанет его обновлять."""
    now = datetime.now(UTC).isoformat()
    client.set(HEARTBEAT_KEY, now, ex=ttl_seconds)
    return now


async def worker_status(client: redis_async.Redis, stale_after_seconds: int) -> ComponentStatus:
    """Определить состояние воркера по времени последней отметки."""
    raw = await client.get(HEARTBEAT_KEY)
    if not raw:
        return ComponentStatus(status="unknown", message="Фоновый воркер ещё не отмечался. Если это длится дольше пары минут, проверьте контейнеры worker и beat.")
    try:
        last = datetime.fromisoformat(raw)
    except ValueError:
        return ComponentStatus(status="error", message="Отметка воркера повреждена.")
    age = (datetime.now(UTC) - last).total_seconds()
    if age > stale_after_seconds:
        return ComponentStatus(status="stale", message=f"Фоновый воркер не отвечает уже {int(age)} с.")
    return ComponentStatus(status="ok", message=f"Фоновый воркер работает, последняя отметка {int(age)} с назад.")
