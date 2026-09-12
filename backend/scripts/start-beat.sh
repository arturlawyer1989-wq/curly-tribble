#!/bin/sh
# Планировщик Celery: запускает задачи по расписанию. Pid-файл нужен для проверки здоровья контейнера.
set -e
rm -f /tmp/celerybeat.pid
exec celery -A app.workers.celery_app beat --loglevel=INFO --schedule=/tmp/celerybeat-schedule --pidfile=/tmp/celerybeat.pid
