"""Чтение и первичное заполнение настроек магазина."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models.shop import SHOP_ROW_ID, ShopSettings


def defaults_from_settings(settings: Settings) -> dict[str, str]:
    """Начальные значения из переменных окружения (.env)."""
    return {
        "name": settings.shop_name,
        "short_name": settings.shop_short_name,
        "city": settings.shop_city,
        "phone": settings.shop_phone,
        "address": settings.shop_address,
        "work_hours": settings.shop_work_hours,
        "legal_name": settings.shop_legal_name,
        "inn": settings.shop_inn,
        "email": settings.shop_email,
    }


async def get_shop(session: AsyncSession) -> ShopSettings | None:
    return await session.scalar(select(ShopSettings).where(ShopSettings.id == SHOP_ROW_ID))


async def ensure_shop(session: AsyncSession, settings: Settings) -> tuple[ShopSettings, bool]:
    """Создать строку настроек, если её ещё нет. Возвращает (строка, создана_ли_сейчас)."""
    existing = await get_shop(session)
    if existing is not None:
        return existing, False
    shop = ShopSettings(id=SHOP_ROW_ID, **defaults_from_settings(settings))
    session.add(shop)
    await session.commit()
    await session.refresh(shop)
    return shop, True
