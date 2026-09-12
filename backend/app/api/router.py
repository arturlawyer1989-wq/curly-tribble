"""Сборка всех маршрутов API под общим префиксом /api/v1."""

from fastapi import APIRouter

from app.api.admin import auth as admin_auth_api
from app.api.admin import overview as admin_overview_api
from app.api.public import health, shop

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(shop.router)

admin_router = APIRouter(prefix="/admin")
admin_router.include_router(admin_auth_api.router)
admin_router.include_router(admin_overview_api.router)
api_router.include_router(admin_router)
