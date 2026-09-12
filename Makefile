# Короткие команды для работы с магазином. Запуск: make <команда>
.PHONY: up down restart logs ps test-backend test-e2e lint

up:            ## Собрать и запустить все сервисы
	docker compose up -d --build

down:          ## Остановить сервисы (данные сохраняются)
	docker compose down

restart:       ## Перезапустить сервисы
	docker compose restart

logs:          ## Показать логи всех контейнеров
	docker compose logs -f --tail=200

ps:            ## Состояние контейнеров
	docker compose ps

test-backend:  ## Автотесты бэкенда внутри контейнера
	docker compose exec backend pytest

test-e2e:      ## Сквозные тесты в браузере (нужен Node.js на этом компьютере)
	cd frontend && npx playwright test

lint:          ## Проверка кода фронтенда
	cd frontend && npm run lint
