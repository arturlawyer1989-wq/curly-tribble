# ДЕТАЛЬ 24 — интернет-магазин автозапчастей

Магазин запчастей для иномарок в Старобельске. Оплата наличными при получении, заказ только после
подтверждения номера телефона кодом.

## Что нужно для запуска

- Docker с Docker Compose (на сервере: Docker Engine, на компьютере: Docker Desktop).
- Свободный порт 80 (или другой, см. `HTTP_PORT` в `.env`).

## Первый запуск

Linux или macOS (одна команда, сама создаст `.env` и подставит пароль базы):

```bash
./scripts/first_run.sh
```

Windows (PowerShell):

```powershell
copy .env.example .env
# откройте .env и впишите POSTGRES_PASSWORD (любой длинный пароль без пробелов)
docker compose up -d --build
```

Через одну-две минуты сайт открывается по адресу http://localhost (или http://localhost:ПОРТ, если меняли `HTTP_PORT`).

Состояние сервисов: http://localhost/health (приложение, база данных, Redis и фоновый воркер).

## Панель управления

Адрес: http://localhost/admin (на сервере: https://ваш-домен/admin).

Первый владелец создаётся автоматически при первом запуске из `.env`: логин `ADMIN_LOGIN`, пароль `ADMIN_PASSWORD`.
Если при первом запуске пароль был пустым, создайте владельца командой (магазин должен быть запущен):

```bash
docker compose exec backend python scripts/create_admin.py --login owner --name "Ваше имя" --role owner
```

Сменить забытый пароль:

```bash
docker compose exec backend python scripts/create_admin.py --login owner --reset-password
```

Добавить менеджера с ограниченными правами: та же команда с `--role manager`.
На Linux и macOS есть короткая форма: `./scripts/create_admin.sh --login owner --reset-password`.

## Повседневные команды

| Что сделать | Команда |
|---|---|
| Запустить или обновить после изменений | `docker compose up -d --build` |
| Остановить (данные сохраняются) | `docker compose down` |
| Посмотреть логи всех сервисов | `docker compose logs --tail=200` |
| Смотреть логи одного сервиса вживую (например, backend) | `docker compose logs -f backend` |
| Состояние контейнеров | `docker compose ps` |
| Автотесты бэкенда | `docker compose exec backend pytest` |
| Проверить, что миграции базы применены | `docker compose exec backend alembic current` |
| Сквозные тесты в браузере | `cd frontend && npm ci && npx playwright install chromium && npx playwright test` |

Те же команды доступны через `make up`, `make down`, `make logs`, `make test-backend`.

## Где что лежит

- `backend/` — API на FastAPI, фоновые задачи Celery, миграции базы, тесты pytest.
- `frontend/` — сайт на Next.js, дизайн-система из прототипа, тесты Playwright.
- `nginx/` — веб-сервер: маршрутизация, ограничение частоты запросов.
- `postgres/init/` — создание тестовой базы при первом запуске сервиса `db` (PostgreSQL).
- `docs/` — прототип-эталон `prototype-v8.html` и описание архитектуры.
- `scripts/` — скрипт первого запуска.
- `.env.example` — все настройки с пояснениями; рабочий файл `.env` в git не попадает.

## Если что-то не так

- Сайт не открывается: `docker compose ps` покажет, какой сервис не поднялся (frontend, backend, db, redis, nginx, worker, beat), а `docker compose logs имя_сервиса` покажет причину.
- Docker не может скачать образы (в России Docker Hub бывает недоступен): добавьте зеркало в
  `/etc/docker/daemon.json`, например `{"registry-mirrors": ["https://mirror.gcr.io"]}`, и перезапустите Docker.
- Порт 80 занят: поменяйте `HTTP_PORT` в `.env` и выполните `docker compose up -d`.
