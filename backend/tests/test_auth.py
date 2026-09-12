"""Вход в панель управления: пароли, токены, обновление сессии, роли, защита от перебора."""

from datetime import timedelta

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.db import get_session_factory
from app.core.security import create_access_token
from app.models import AdminAuditLog, AdminSession, AdminUser, Brand, Product
from app.services.admin_auth import ensure_owner
from tests.conftest import MANAGER_PASSWORD, OWNER_PASSWORD

CSRF = {"X-Requested-With": "XMLHttpRequest"}


async def login(client: AsyncClient, login_name: str, password: str):
    return await client.post("/api/v1/admin/auth/login", json={"login": login_name, "password": password})


async def test_login_success_sets_cookies_and_returns_user(client: AsyncClient, owner: AdminUser) -> None:
    response = await login(client, "owner", OWNER_PASSWORD)
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["login"] == "owner"
    assert body["user"]["role"] == "owner"
    assert body["user"]["full_name"] == "Артур"
    assert "d24_access" in response.cookies and "d24_refresh" in response.cookies
    set_cookie = " ".join(response.headers.get_list("set-cookie"))
    assert "HttpOnly" in set_cookie and "SameSite=lax" in set_cookie


async def test_login_wrong_password_gives_russian_message(client: AsyncClient, owner: AdminUser) -> None:
    response = await login(client, "owner", "неверный")
    assert response.status_code == 401
    assert response.json()["error"] == {"code": "login_failed", "message": "Неверный логин или пароль."}
    assert "d24_access" not in response.cookies


async def test_unknown_login_gets_same_message(client: AsyncClient, owner: AdminUser) -> None:
    response = await login(client, "nobody", "whatever")
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Неверный логин или пароль."


async def test_inactive_user_cannot_login(client: AsyncClient, owner: AdminUser) -> None:
    async with get_session_factory()() as session:
        user = await session.get(AdminUser, owner.id)
        user.is_active = False
        await session.commit()
    response = await login(client, "owner", OWNER_PASSWORD)
    assert response.status_code == 401


async def test_login_is_rate_limited(client: AsyncClient, owner: AdminUser) -> None:
    limit = get_settings().login_attempts_per_minute
    for _ in range(limit):
        assert (await login(client, "owner", "wrong")).status_code == 401
    response = await login(client, "owner", OWNER_PASSWORD)
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "too_many_attempts"
    assert "Подождите" in response.json()["error"]["message"]
    assert response.headers.get("retry-after")


async def test_me_requires_login(client: AsyncClient) -> None:
    response = await client.get("/api/v1/admin/auth/me")
    assert response.status_code == 401
    assert response.json()["error"] == {"code": "unauthorized", "message": "Нужно войти в панель управления."}


async def test_me_works_with_cookie_after_login(client: AsyncClient, owner: AdminUser) -> None:
    await login(client, "owner", OWNER_PASSWORD)
    response = await client.get("/api/v1/admin/auth/me")
    assert response.status_code == 200
    assert response.json()["login"] == "owner"


async def test_expired_token_gives_401_session_expired(client: AsyncClient, owner: AdminUser) -> None:
    token, _ = create_access_token(secret=get_settings().secret_key, user_id=owner.id, role="owner", login="owner", lifetime=timedelta(minutes=-1))
    response = await client.get("/api/v1/admin/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["error"] == {"code": "session_expired", "message": "Сессия истекла, войдите снова."}


async def test_foreign_or_tampered_token_gives_401(client: AsyncClient, owner: AdminUser) -> None:
    foreign = jwt.encode({"sub": str(owner.id), "role": "owner", "type": "access", "exp": 4102444800}, "another-secret-key-of-someone-else-123456", algorithm="HS256")
    response = await client.get("/api/v1/admin/overview", headers={"Authorization": f"Bearer {foreign}"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"
    valid, _ = create_access_token(secret=get_settings().secret_key, user_id=owner.id, role="owner", login="owner", lifetime=timedelta(minutes=5))
    tampered = valid[:-4] + "abcd"
    response = await client.get("/api/v1/admin/overview", headers={"Authorization": f"Bearer {tampered}"})
    assert response.status_code == 401
    response = await client.get("/api/v1/admin/overview", headers={"Cookie": "d24_access=foreign-token-of-someone-else"})
    assert response.status_code == 401


async def test_refresh_rotates_session_and_rejects_old_token(client: AsyncClient, owner: AdminUser) -> None:
    first = await login(client, "owner", OWNER_PASSWORD)
    old_refresh = first.cookies["d24_refresh"]
    refreshed = await client.post("/api/v1/admin/auth/refresh", headers=CSRF)
    assert refreshed.status_code == 200
    new_refresh = refreshed.cookies["d24_refresh"]
    assert new_refresh != old_refresh
    client.cookies.set("d24_refresh", old_refresh)
    replay = await client.post("/api/v1/admin/auth/refresh", headers=CSRF)
    assert replay.status_code == 401
    async with get_session_factory()() as session:
        revoked = await session.scalar(select(func.count()).select_from(AdminSession).where(AdminSession.revoked_at.is_not(None)))
    assert revoked == 1


async def test_logout_revokes_session_and_clears_cookies(client: AsyncClient, owner: AdminUser) -> None:
    await login(client, "owner", OWNER_PASSWORD)
    response = await client.post("/api/v1/admin/auth/logout", headers=CSRF)
    assert response.status_code == 204
    cleared = [h for h in response.headers.get_list("set-cookie") if 'Max-Age=0' in h or "expires" in h.lower()]
    assert len(cleared) == 2, "должны удаляться обе cookie"
    assert not client.cookies.get("d24_access") and not client.cookies.get("d24_refresh")
    assert (await client.get("/api/v1/admin/auth/me")).status_code == 401
    assert (await client.post("/api/v1/admin/auth/refresh", headers=CSRF)).status_code == 401


async def test_cookie_auth_requires_csrf_header_for_changes(client: AsyncClient, owner: AdminUser) -> None:
    await login(client, "owner", OWNER_PASSWORD)
    response = await client.post("/api/v1/admin/auth/logout")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "csrf_rejected"
    assert (await client.get("/api/v1/admin/auth/me")).status_code == 200


async def test_users_list_is_owner_only(client: AsyncClient, owner: AdminUser, manager: AdminUser) -> None:
    await login(client, "manager", MANAGER_PASSWORD)
    response = await client.get("/api/v1/admin/users")
    assert response.status_code == 403
    assert response.json()["error"]["message"] == "Это действие доступно только владельцу."
    await client.post("/api/v1/admin/auth/logout", headers=CSRF)
    await login(client, "owner", OWNER_PASSWORD)
    response = await client.get("/api/v1/admin/users")
    assert response.status_code == 200
    assert [u["login"] for u in response.json()] == ["owner", "manager"]


async def test_overview_counts_reflect_database(client: AsyncClient, owner: AdminUser) -> None:
    assert (await client.get("/api/v1/admin/overview")).status_code == 401
    async with get_session_factory()() as session:
        brand = Brand(name="MANN-FILTER", name_normalized="MANNFILTER")
        session.add(brand)
        await session.flush()
        session.add(Product(brand_id=brand.id, article="W 712/94", article_normalized="W71294", name="Фильтр масляный"))
        await session.commit()
    await login(client, "owner", OWNER_PASSWORD)
    body = (await client.get("/api/v1/admin/overview")).json()
    counts = {s["key"]: s["count"] for s in body["sections"]}
    assert counts["products"] == 1 and counts["brands"] == 1 and counts["orders"] == 0
    assert body["orders_by_status"]["new"] == 0


async def test_audit_log_records_login_and_failure(client: AsyncClient, owner: AdminUser) -> None:
    await login(client, "owner", "wrong")
    await login(client, "owner", OWNER_PASSWORD)
    async with get_session_factory()() as session:
        actions = (await session.scalars(select(AdminAuditLog.action).order_by(AdminAuditLog.id))).all()
    assert actions == ["login_failed", "login"]


async def test_ensure_owner_from_env_runs_once() -> None:
    settings = get_settings()
    settings.admin_login = "Owner"
    settings.admin_password = "Env-Password-123"
    try:
        async with get_session_factory()() as session:
            created = await ensure_owner(session, settings)
            assert created is not None and created.login == "owner" and created.role == "owner"
            again = await ensure_owner(session, settings)
            assert again is None
            total = await session.scalar(select(func.count()).select_from(AdminUser))
        assert total == 1
    finally:
        settings.admin_login = ""
        settings.admin_password = ""
