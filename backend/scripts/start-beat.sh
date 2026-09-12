#!/bin/sh
# Планировщик Celery: запускает задачи по расписанию.
set -e
exec celery -A app.workers.celery_app beat --loglevel=INFO --schedule=/tmp/celerybeat-schedule
