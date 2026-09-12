"""Все таблицы базы данных. Импорт здесь нужен, чтобы Alembic видел модели."""

from app.core.db import Base
from app.models.shop import ShopSettings

__all__ = ["Base", "ShopSettings"]
