#!/bin/sh
# Фоновый воркер Celery: импорт прайсов, уведомления, служебные задачи.
set -e
exec celery -A app.workers.celery_app worker --loglevel=INFO --concurrency=2
