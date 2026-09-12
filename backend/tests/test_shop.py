"""Публичные данные магазина и первичное заполнение."""

from httpx import AsyncClient
from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.db import get_session_factory
from app.models.shop import ShopSettings
from app.schemas.shop import phone_to_href
from app.seeds.apply import apply_seeds
from app.services.shop import ensure_shop


async def test_shop_returns_env_defaults_when_table_is_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/shop")
    assert response.status_code == 200
    body = response.json()
    settings = get_settings()
    assert body["name"] == settings.shop_name
    assert body["short_name"] == settings.shop_short_name
    # Телефон берётся из .env, поэтому сравниваем с настройками, а не с пустой строкой
    assert body["phone"] == settings.shop_phone
    assert body["phone_href"] == phone_to_href(settings.shop_phone)


async def test_shop_returns_stored_values(client: AsyncClient) -> None:
    async with get_session_factory()() as session:
        shop, created = await ensure_shop(session, get_settings())
        assert created is True
        shop.phone = "+7 959 123-45-67"
        shop.address = "г. Старобельск, ул. Ленина, 1"
        await session.commit()
    body = (await client.get("/api/v1/shop")).json()
    assert body["phone"] == "+7 959 123-45-67"
    assert body["phone_href"] == "tel:+79591234567"
    assert body["address"] == "г. Старобельск, ул. Ленина, 1"


async def test_ensure_shop_is_idempotent() -> None:
    async with get_session_factory()() as session:
        _, first = await ensure_shop(session, get_settings())
        _, second = await ensure_shop(session, get_settings())
        count = await session.scalar(select(func.count()).select_from(ShopSettings))
    assert (first, second) == (True, False)
    assert count == 1


async def test_seed_script_creates_row_once() -> None:
    await apply_seeds()
    await apply_seeds()
    async with get_session_factory()() as session:
        count = await session.scalar(select(func.count()).select_from(ShopSettings))
    assert count == 1


def test_phone_to_href_formats() -> None:
    assert phone_to_href("+7 959 000-00-00") == "tel:+79590000000"
    assert phone_to_href("8 (959) 000-00-00") == "tel:+79590000000"
    assert phone_to_href("9590000000") == "tel:+79590000000"
    assert phone_to_href("") == ""
    assert phone_to_href("нет") == ""
