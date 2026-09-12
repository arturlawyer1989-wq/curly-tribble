"""Вход сотрудников: проверка пароля, выпуск и обновление токенов, журнал действий."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    password_needs_rehash,
    verify_password,
)
from app.models.admin import AdminAuditLog, AdminSession, AdminUser

# Хеш заведомо неверного пароля: проверяем его, когда логин не найден,
# чтобы время ответа не выдавало, существует ли такой сотрудник
_DUMMY_HASH = hash_password("dummy-password-for-timing")


@dataclass(frozen=True)
class IssuedTokens:
    access_token: str
    access_expires_at: datetime
    refresh_token: str
    refresh_expires_at: datetime


@dataclass(frozen=True)
class RequestMeta:
    ip: str = ""
    user_agent: str = ""


async def authenticate(session: AsyncSession, login: str, password: str) -> AdminUser | None:
    """Вернуть сотрудника, если логин и пароль верны и учётная запись активна."""
    user = await session.scalar(select(AdminUser).where(AdminUser.login == login.strip().lower()))
    if user is None:
        verify_password(password, _DUMMY_HASH)
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    if password_needs_rehash(user.password_hash):
        user.password_hash = hash_password(password)
    return user


async def issue_tokens(session: AsyncSession, settings: Settings, user: AdminUser, meta: RequestMeta) -> IssuedTokens:
    """Выпустить токен доступа и создать сессию обновления."""
    access_token, access_expires_at = create_access_token(
        secret=settings.secret_key,
        user_id=user.id,
        role=user.role,
        login=user.login,
        lifetime=timedelta(minutes=settings.access_token_minutes),
    )
    refresh_token = generate_refresh_token()
    refresh_expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_days)
    session.add(
        AdminSession(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=refresh_expires_at,
            user_agent=meta.user_agent[:255],
            ip=meta.ip[:45],
        )
    )
    user.last_login_at = datetime.now(UTC)
    await session.flush()
    return IssuedTokens(access_token, access_expires_at, refresh_token, refresh_expires_at)


async def find_live_session(session: AsyncSession, refresh_token: str) -> AdminSession | None:
    """Сессия по токену обновления, если она не отозвана и не истекла."""
    admin_session = await session.scalar(select(AdminSession).where(AdminSession.token_hash == hash_refresh_token(refresh_token)))
    if admin_session is None or admin_session.revoked_at is not None:
        return None
    if admin_session.expires_at <= datetime.now(UTC):
        return None
    return admin_session


async def rotate_session(session: AsyncSession, settings: Settings, refresh_token: str, meta: RequestMeta) -> tuple[AdminUser, IssuedTokens] | None:
    """Обменять токен обновления на новую пару. Старый токен сразу отзывается."""
    admin_session = await find_live_session(session, refresh_token)
    if admin_session is None:
        return None
    user = await session.get(AdminUser, admin_session.user_id)
    if user is None or not user.is_active:
        return None
    admin_session.revoked_at = datetime.now(UTC)
    tokens = await issue_tokens(session, settings, user, meta)
    return user, tokens


async def revoke_session(session: AsyncSession, refresh_token: str) -> bool:
    admin_session = await find_live_session(session, refresh_token)
    if admin_session is None:
        return False
    admin_session.revoked_at = datetime.now(UTC)
    await session.flush()
    return True


async def audit(session: AsyncSession, *, admin_id: int | None, action: str, ip: str = "", entity: str = "", entity_id: str = "", details: dict | None = None) -> None:
    """Запись в журнал действий."""
    session.add(AdminAuditLog(admin_id=admin_id, action=action, entity=entity, entity_id=entity_id, details=details or {}, ip=ip[:45]))
    await session.flush()


async def create_admin_user(session: AsyncSession, *, login: str, password: str, full_name: str, role: str) -> AdminUser:
    user = AdminUser(login=login.strip().lower(), password_hash=hash_password(password), full_name=full_name.strip(), role=role)
    session.add(user)
    await session.flush()
    return user


async def ensure_owner(session: AsyncSession, settings: Settings) -> AdminUser | None:
    """Создать первого владельца из .env, если сотрудников ещё нет. Возвращает созданного или None."""
    existing = await session.scalar(select(AdminUser.id).limit(1))
    if existing is not None:
        return None
    if not settings.admin_login or not settings.admin_password:
        return None
    user = await create_admin_user(session, login=settings.admin_login, password=settings.admin_password, full_name=settings.admin_name, role="owner")
    await session.commit()
    return user
