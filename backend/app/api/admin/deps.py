"""Зависимости доступа к панели управления."""

from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.core.security import TokenError, decode_access_token
from app.models.admin import AdminUser

ACCESS_COOKIE = "d24_access"
REFRESH_COOKIE = "d24_refresh"
CSRF_HEADER = "x-requested-with"

UNAUTHORIZED = {"code": "unauthorized", "message": "Нужно войти в панель управления."}
SESSION_EXPIRED = {"code": "session_expired", "message": "Сессия истекла, войдите снова."}
FORBIDDEN = {"code": "forbidden", "message": "Это действие доступно только владельцу."}
CSRF_REJECTED = {"code": "csrf_rejected", "message": "Запрос отклонён. Обновите страницу и повторите действие."}


@dataclass(frozen=True)
class CurrentAdmin:
    user: AdminUser
    via_cookie: bool


def _extract_token(request: Request) -> tuple[str | None, bool]:
    """Токен из заголовка Authorization: Bearer или из cookie. Второе значение: пришёл ли он из cookie."""
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:].strip(), False
    cookie = request.cookies.get(ACCESS_COOKIE)
    if cookie:
        return cookie, True
    return None, False


async def get_current_admin(request: Request, session: AsyncSession = Depends(get_session)) -> CurrentAdmin:
    token, via_cookie = _extract_token(request)
    if not token:
        raise HTTPException(status_code=401, detail=UNAUTHORIZED)
    try:
        payload = decode_access_token(token, secret=get_settings().secret_key)
    except TokenError as exc:
        raise HTTPException(status_code=401, detail=SESSION_EXPIRED if exc.reason == "expired" else UNAUTHORIZED) from exc
    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail=UNAUTHORIZED) from None
    user = await session.get(AdminUser, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail=UNAUTHORIZED)
    # Защита от подделки запросов: при входе по cookie изменяющие запросы должны нести служебный заголовок
    if via_cookie and request.method not in ("GET", "HEAD", "OPTIONS") and request.headers.get(CSRF_HEADER, "").lower() != "xmlhttprequest":
        raise HTTPException(status_code=403, detail=CSRF_REJECTED)
    return CurrentAdmin(user=user, via_cookie=via_cookie)


async def require_owner(current: CurrentAdmin = Depends(get_current_admin)) -> CurrentAdmin:
    if current.user.role != "owner":
        raise HTTPException(status_code=403, detail=FORBIDDEN)
    return current


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""
