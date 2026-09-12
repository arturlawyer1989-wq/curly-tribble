"""Фоновые задачи на Celery: очередь в Redis, расписание в beat."""

from celery import Celery

from app.core.config import get_settings
from app.core.logging import setup_logging

settings = get_settings()
setup_logging(settings.log_level)

celery_app = Celery("detal24", broker=settings.celery_broker, include=["app.workers.tasks"])
celery_app.conf.update(
    timezone="Europe/Moscow",
    enable_utc=True,
    task_ignore_result=True,
    task_default_queue="default",
    broker_connection_retry_on_startup=True,
    worker_hijack_root_logger=False,
    beat_schedule={
        "worker-heartbeat": {
            "task": "app.workers.tasks.heartbeat",
            "schedule": float(settings.worker_heartbeat_interval_seconds),
        },
    },
)
