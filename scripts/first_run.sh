#!/usr/bin/env bash
# Первый запуск магазина одной командой: создаёт .env, собирает и запускает контейнеры, ждёт готовности.
# Повторный запуск безопасен: существующие настройки и данные не трогаются.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Создан файл .env из .env.example"
fi

if grep -qE '^POSTGRES_PASSWORD=$' .env; then
  password=$(python3 -c 'import secrets; print(secrets.token_hex(16))' 2>/dev/null || openssl rand -hex 16)
  sed -i.bak "s/^POSTGRES_PASSWORD=$/POSTGRES_PASSWORD=${password}/" .env && rm -f .env.bak
  echo "В .env записан случайный пароль базы данных"
fi

docker compose up -d --build

port=$(grep -E '^HTTP_PORT=' .env | cut -d= -f2 | tr -d '[:space:]')
port=${port:-80}
echo "Жду, пока сайт ответит на http://localhost:${port} ..."
for _ in $(seq 1 60); do
  if curl -fsS "http://localhost:${port}/healthz" >/dev/null 2>&1; then
    echo "Готово. Откройте в браузере: http://localhost:${port}"
    exit 0
  fi
  sleep 3
done
echo "Сайт не ответил за 3 минуты. Посмотрите логи командой: docker compose logs --tail=100" >&2
exit 1
