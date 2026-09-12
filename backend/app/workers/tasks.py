"""Задачи фонового воркера."""

import logging

from celery.signals import worker_ready

from app.core.config import get_settings
from app.core.redis import get_sync_redis
from app.services.heartbeat import write_heartbeat
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.tasks.heartbeat")
def heartbeat() -> str:
    """Отметиться в Redis: по этой отметке страница состояния понимает, что воркер жив."""
    settings = get_settings()
    client = get_sync_redis()
    try:
        stamp = write_heartbeat(client, ttl_seconds=settings.worker_heartbeat_stale_after_seconds)
    finally:
        client.close()
    logger.debug("Отметка воркера записана: %s", stamp)
    return stamp


@worker_ready.connect
def send_first_heartbeat(**_: object) -> None:
    """Воркер отмечается сразу после запуска, не дожидаясь первого тика расписания."""
    heartbeat.delay()
