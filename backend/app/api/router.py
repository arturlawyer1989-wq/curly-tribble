"""Сборка всех маршрутов API под общим префиксом /api/v1."""

from fastapi import APIRouter

from app.api.public import health, shop

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(shop.router)
