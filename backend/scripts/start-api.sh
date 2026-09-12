#!/bin/sh
# Запуск API: миграции базы, начальные данные, затем сервер.
set -e

attempt=1
until alembic upgrade head; do
  if [ "$attempt" -ge 10 ]; then
    echo "Не удалось применить миграции за 10 попыток, останавливаюсь" >&2
    exit 1
  fi
  echo "База ещё не готова, повторяю через 3 секунды (попытка $attempt из 10)..."
  attempt=$((attempt + 1))
  sleep 3
done

python -m app.seeds.apply
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*"
