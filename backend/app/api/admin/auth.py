"""Вход, обновление сессии, выход и текущий сотрудник."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin.deps import ACCESS_COOKIE, CSRF_HEADER, CSRF_REJECTED, REFRESH_COOKIE, UNAUTHORIZED, CurrentAdmin, client_ip, get_current_admin
from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.core.redis import get_redis
from app.schemas.admin import AdminUserPublic, LoginRequest, LoginResponse
from app.services import admin_auth
from app.services.admin_auth import IssuedTokens, RequestMeta
from app.services.ratelimit import hit, reset

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Панель: вход"])

LOGIN_FAILED = {"code": "login_failed", "message": "Неверный логин или пароль."}
TOO_MANY_ATTEMPTS = {"code": "too_many_attempts", "message": "Слишком много попыток входа. Подождите минуту и попробуйте снова."}


def _meta(request: Request) -> RequestMeta:
    return RequestMeta(ip=client_ip(request), user_agent=request.headers.get("user-agent", ""))


def set_auth_cookies(response: Response, request: Request, tokens: IssuedTokens, settings: Settings) -> None:
    """Токены живут в httpOnly-cookie: скрипты страницы их не видят, браузер шлёт сам."""
    secure = request.url.scheme == "https"
    response.set_cookie(ACCESS_COOKIE, tokens.access_token, max_age=settings.access_token_minutes * 60, httponly=True, samesite="lax", secure=secure, path="/")
    response.set_cookie(REFRESH_COOKIE, tokens.refresh_token, max_age=settings.refresh_token_days * 86400, httponly=True, samesite="lax", secure=secure, path="/")


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/")


@router.post("/login", response_model=LoginResponse, summary="Вход по логину и паролю")
async def login(payload: LoginRequest, request: Request, response: Response, session: AsyncSession = Depends(get_session)) -> LoginResponse:
    settings = get_settings()
    login_key = f"d24:login:attempts:{payload.login.strip().lower()}"
    ip_key = f"d24:login:ip:{client_ip(request)}"
    redis = get_redis()
    allowed_login, retry_login = await hit(redis, login_key, settings.login_attempts_per_minute, 60)
    allowed_ip, retry_ip = await hit(redis, ip_key, settings.login_attempts_per_minute * 4, 60)
    if not allowed_login or not allowed_ip:
        raise HTTPException(status_code=429, detail=TOO_MANY_ATTEMPTS, headers={"Retry-After": str(max(retry_login, retry_ip))})

    user = await admin_auth.authenticate(session, payload.login, payload.password)
    if user is None:
        await admin_auth.audit(session, admin_id=None, action="login_failed", ip=client_ip(request), details={"login": payload.login.strip().lower()[:64]})
        await session.commit()
        logger.warning("Неудачный вход в панель: логин %r", payload.login[:64])
        raise HTTPException(status_code=401, detail=LOGIN_FAILED)

    tokens = await admin_auth.issue_tokens(session, settings, user, _meta(request))
    await admin_auth.audit(session, admin_id=user.id, action="login", ip=client_ip(request))
    await session.commit()
    await reset(redis, login_key)
    set_auth_cookies(response, request, tokens, settings)
    return LoginResponse(user=AdminUserPublic.model_validate(user), access_expires_at=tokens.access_expires_at)


@router.post("/refresh", response_model=LoginResponse, summary="Обновить сессию")
async def refresh(request: Request, response: Response, session: AsyncSession = Depends(get_session)) -> LoginResponse:
    settings = get_settings()
    refresh_token = request.cookies.get(REFRESH_COOKIE) or request.headers.get("x-refresh-token", "")
    if not refresh_token:
        raise HTTPException(status_code=401, detail=UNAUTHORIZED)
    rotated = await admin_auth.rotate_session(session, settings, refresh_token, _meta(request))
    if rotated is None:
        clear_auth_cookies(response)
        raise HTTPException(status_code=401, detail={"code": "session_expired", "message": "Сессия истекла, войдите снова."})
    user, tokens = rotated
    await session.commit()
    set_auth_cookies(response, request, tokens, settings)
    return LoginResponse(user=AdminUserPublic.model_validate(user), access_expires_at=tokens.access_expires_at)


@router.post("/logout", status_code=204, summary="Выход")
async def logout(request: Request, session: AsyncSession = Depends(get_session)) -> Response:
    # Выход возможен и с просроченным токеном доступа: достаточно cookie сессии
    if request.cookies.get(ACCESS_COOKIE) and request.headers.get(CSRF_HEADER, "").lower() != "xmlhttprequest":
        raise HTTPException(status_code=403, detail=CSRF_REJECTED)
    refresh_token = request.cookies.get(REFRESH_COOKIE) or request.headers.get("x-refresh-token", "")
    if refresh_token:
        admin_session = await admin_auth.find_live_session(session, refresh_token)
        if admin_session is not None:
            await admin_auth.revoke_session(session, refresh_token)
            await admin_auth.audit(session, admin_id=admin_session.user_id, action="logout", ip=client_ip(request))
            await session.commit()
    response = Response(status_code=204)
    clear_auth_cookies(response)
    return response


@router.get("/me", response_model=AdminUserPublic, summary="Текущий сотрудник")
async def me(current: CurrentAdmin = Depends(get_current_admin)) -> AdminUserPublic:
    return AdminUserPublic.model_validate(current.user)
