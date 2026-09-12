"""Проверка состояния: приложение, база, Redis, фоновый воркер.

Доступна по двум адресам: /health (для мониторинга) и /api/v1/health (для сайта).
"""

import asyncio
import logging
from datetime import UTC, datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app import __version__
from app.core.config import get_settings
from app.core.db import get_engine
from app.core.redis import get_redis
from app.schemas.health import ComponentStatus, HealthResponse
from app.services.heartbeat import worker_status

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Состояние"])

CHECK_TIMEOUT = 3.0


async def _check_database() -> ComponentStatus:
    try:
        async with get_engine().connect() as conn:
            await asyncio.wait_for(conn.execute(text("SELECT 1")), timeout=CHECK_TIMEOUT)
        return ComponentStatus(status="ok", message="База данных работает.")
    except Exception as exc:  # noqa: BLE001 - любая ошибка подключения должна попасть в ответ
        logger.error("База данных недоступна: %s", exc)
        return ComponentStatus(status="error", message="База данных недоступна.")


async def _check_redis() -> ComponentStatus:
    try:
        await asyncio.wait_for(get_redis().ping(), timeout=CHECK_TIMEOUT)
        return ComponentStatus(status="ok", message="Redis работает.")
    except Exception as exc:  # noqa: BLE001
        logger.error("Redis недоступен: %s", exc)
        return ComponentStatus(status="error", message="Redis недоступен.")


@router.get("/health", response_model=HealthResponse, summary="Состояние сервисов")
async def health() -> JSONResponse:
    settings = get_settings()
    database, redis_state = await asyncio.gather(_check_database(), _check_redis())
    if redis_state.status == "ok":
        worker = await worker_status(get_redis(), settings.worker_heartbeat_stale_after_seconds)
    else:
        worker = ComponentStatus(status="unknown", message="Состояние воркера неизвестно: Redis недоступен.")

    if database.status == "error" or redis_state.status == "error":
        overall = "error"
    elif worker.status != "ok":
        overall = "degraded"
    else:
        overall = "ok"

    body = HealthResponse(
        status=overall,
        app=ComponentStatus(status="ok", message="Приложение работает."),
        db=database,
        redis=redis_state,
        worker=worker,
        version=__version__,
        time=datetime.now(UTC),
    )
    return JSONResponse(status_code=503 if overall == "error" else 200, content=body.model_dump(mode="json"))
