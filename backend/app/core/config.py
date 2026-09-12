"""Настройки приложения.

Все значения читаются из переменных окружения (в Docker они приходят из файла .env).
Секретов в коде нет: пароли и адреса задаются только снаружи.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Полный список настроек с безопасными значениями по умолчанию."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Режим работы: prod на сервере, dev при разработке, test в автотестах
    app_env: Literal["dev", "test", "prod"] = "prod"
    # Уровень подробности логов
    log_level: str = "INFO"

    # Подключение к PostgreSQL (драйвер asyncpg для приложения)
    database_url: str = "postgresql+asyncpg://detal24:detal24@postgres:5432/detal24"
    # Подключение к Redis: коды подтверждения, лимиты, кеш, очередь фоновых задач
    redis_url: str = "redis://redis:6379/0"
    # Очередь Celery; если не задана, используется тот же Redis
    celery_broker_url: str = ""

    # Как часто фоновый воркер отмечается «живым» и через сколько секунд считать его пропавшим
    worker_heartbeat_interval_seconds: int = Field(default=60, ge=5)
    worker_heartbeat_stale_after_seconds: int = Field(default=180, ge=10)

    # Начальные данные магазина. Применяются один раз при первом запуске,
    # дальше редактируются в админке (появится на этапе админки).
    shop_name: str = "ДЕТАЛЬ 24"
    shop_short_name: str = "Д24"
    shop_city: str = "Старобельск"
    shop_phone: str = ""
    shop_address: str = ""
    shop_work_hours: str = "Пн–Сб 9:00–18:00"
    shop_legal_name: str = ""
    shop_inn: str = ""
    shop_email: str = ""

    @property
    def sync_database_url(self) -> str:
        """Адрес базы для Alembic и Celery: те же данные, но синхронный драйвер psycopg."""
        return self.database_url.replace("+asyncpg", "+psycopg")

    @property
    def celery_broker(self) -> str:
        """Адрес очереди задач: отдельный, если задан, иначе общий Redis."""
        return self.celery_broker_url or self.redis_url

    @property
    def is_dev(self) -> bool:
        return self.app_env == "dev"


@lru_cache
def get_settings() -> Settings:
    """Настройки читаются один раз и переиспользуются."""
    return Settings()
