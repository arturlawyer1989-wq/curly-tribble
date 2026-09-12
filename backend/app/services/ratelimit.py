"""Простое ограничение частоты через Redis: не больше N событий за окно."""

import redis.asyncio as redis_async


async def hit(client: redis_async.Redis, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
    """Засчитать событие. Возвращает (разрешено, через сколько секунд снова можно)."""
    count = await client.incr(key)
    if count == 1:
        await client.expire(key, window_seconds)
    if count > limit:
        ttl = await client.ttl(key)
        return False, max(int(ttl), 1)
    return True, 0


async def reset(client: redis_async.Redis, key: str) -> None:
    await client.delete(key)
