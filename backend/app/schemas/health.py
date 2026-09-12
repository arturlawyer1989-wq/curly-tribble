"""Ответ проверки состояния сервисов."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

ComponentState = Literal["ok", "error", "stale", "unknown"]


class ComponentStatus(BaseModel):
    status: ComponentState
    message: str


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "error"]
    app: ComponentStatus
    db: ComponentStatus
    redis: ComponentStatus
    worker: ComponentStatus
    version: str
    time: datetime
