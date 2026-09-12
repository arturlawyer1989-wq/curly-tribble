"""Первичное заполнение базы. Запуск: python -m app.seeds.apply. Повторный запуск ничего не ломает."""

import asyncio
import json
import logging
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.db import dispose_engine, get_session_factory
from app.core.logging import setup_logging
from app.models import AdminUser, DeliveryZone, MarkupRule, Scheme, SchemePoint, SchemeSystem, VehicleBrand
from app.services.admin_auth import ensure_owner
from app.services.shop import ensure_shop

logger = logging.getLogger("app.seeds")
DATA_DIR = Path(__file__).parent / "data"

# Зоны доставки из прототипа; цены и расписание владелец правит в панели управления
DELIVERY_ZONES = (
    {"code": "СБ-С", "title": "Старобельск, самовывоз", "description": "Пункт выдачи магазина, Пн–Сб 9:00–18:00", "kind": "pickup", "price": "0", "free_from": None},
    {"code": "СБ-К", "title": "Старобельск, курьер", "description": "В день готовности или на следующий", "kind": "courier", "price": "200", "free_from": "5000"},
    {"code": "СВ", "title": "Сватово, Кременная", "description": "Маршрут по вторникам и пятницам", "kind": "route", "price": "300", "free_from": None},
    {"code": "МЛ", "title": "Меловое, Беловодск, Марковка", "description": "Маршрут по средам и субботам", "kind": "route", "price": "350", "free_from": None},
    {"code": "ОС", "title": "Остальные населённые пункты", "description": "По согласованию, попутным маршрутом", "kind": "other", "price": "350", "free_from": None},
)

# Массовые в России марки, названные владельцем; порядок сохранён
VEHICLE_BRANDS = (
    ("Renault", "renault"), ("Hyundai", "hyundai"), ("Kia", "kia"), ("Volkswagen", "volkswagen"), ("Toyota", "toyota"),
    ("Chevrolet", "chevrolet"), ("Skoda", "skoda"), ("Ford", "ford"), ("Honda", "honda"), ("Nissan", "nissan"),
    ("Mitsubishi", "mitsubishi"), ("BMW", "bmw"), ("Mercedes-Benz", "mercedes-benz"), ("Audi", "audi"), ("Lexus", "lexus"),
    ("Chery", "chery"), ("Mazda", "mazda"), ("SsangYong", "ssangyong"),
)


async def ensure_markup_rule(session: AsyncSession) -> bool:
    """Общая наценка 27% с округлением до 10 ₽, как в прототипе."""
    exists = await session.scalar(select(MarkupRule.id).where(MarkupRule.kind == "global").limit(1))
    if exists is not None:
        return False
    session.add(MarkupRule(kind="global", percent=Decimal("27"), rounding=10, priority=0))
    return True


async def ensure_delivery_zones(session: AsyncSession) -> int:
    existing = set((await session.scalars(select(DeliveryZone.code))).all())
    added = 0
    for order, zone in enumerate(DELIVERY_ZONES):
        if zone["code"] in existing:
            continue
        session.add(DeliveryZone(
            code=zone["code"], title=zone["title"], description=zone["description"], kind=zone["kind"],
            price=Decimal(zone["price"]), free_from=Decimal(zone["free_from"]) if zone["free_from"] else None, sort_order=order,
        ))
        added += 1
    return added


async def ensure_vehicle_brands(session: AsyncSession) -> int:
    existing = set((await session.scalars(select(VehicleBrand.slug))).all())
    added = 0
    for order, (name, slug) in enumerate(VEHICLE_BRANDS):
        if slug in existing:
            continue
        session.add(VehicleBrand(name=name, slug=slug, sort_order=order, is_popular=True))
        added += 1
    return added


async def ensure_schemes(session: AsyncSession) -> tuple[int, int, int]:
    """Системы, узлы и позиции схем из прототипа (файл data/schemes.json)."""
    data = json.loads((DATA_DIR / "schemes.json").read_text(encoding="utf-8"))
    systems_added = schemes_added = points_added = 0
    for system_data in data["systems"]:
        system = await session.scalar(select(SchemeSystem).where(SchemeSystem.slug == system_data["slug"]))
        if system is None:
            system = SchemeSystem(slug=system_data["slug"], title=system_data["title"], sort_order=system_data["sort_order"])
            session.add(system)
            await session.flush()
            systems_added += 1
        for scheme_data in system_data["schemes"]:
            scheme = await session.scalar(select(Scheme).where(Scheme.slug == scheme_data["slug"]))
            if scheme is None:
                scheme = Scheme(system_id=system.id, slug=scheme_data["slug"], title=scheme_data["title"], description=scheme_data["description"], sort_order=scheme_data["sort_order"])
                session.add(scheme)
                await session.flush()
                schemes_added += 1
            existing_numbers = set((await session.scalars(select(SchemePoint.number).where(SchemePoint.scheme_id == scheme.id))).all())
            for point in scheme_data["points"]:
                if point["number"] in existing_numbers:
                    continue
                session.add(SchemePoint(scheme_id=scheme.id, number=point["number"], name=point["name"], short_name=point["short_name"], shape_key=point["shape_key"], oem_number=point["oem_number"]))
                points_added += 1
    return systems_added, schemes_added, points_added


async def apply_seeds(settings: Settings | None = None) -> dict[str, int]:
    settings = settings or get_settings()
    result: dict[str, int] = {}
    async with get_session_factory()() as session:
        shop, created = await ensure_shop(session, settings)
        result["shop_created"] = int(created)
        logger.info("Настройки магазина «%s»: %s", shop.name, "созданы" if created else "уже есть")

        owner = await ensure_owner(session, settings)
        result["owner_created"] = int(owner is not None)
        if owner is not None:
            logger.info("Создан владелец панели управления с логином «%s»", owner.login)
        else:
            admins = await session.scalar(select(func.count()).select_from(AdminUser))
            if not admins:
                logger.warning("Сотрудников панели управления нет: задайте ADMIN_LOGIN и ADMIN_PASSWORD в .env или выполните scripts/create_admin.py")

        result["markup_rule_created"] = int(await ensure_markup_rule(session))
        result["delivery_zones_added"] = await ensure_delivery_zones(session)
        result["vehicle_brands_added"] = await ensure_vehicle_brands(session)
        systems, schemes, points = await ensure_schemes(session)
        result.update({"scheme_systems_added": systems, "schemes_added": schemes, "scheme_points_added": points})
        await session.commit()
    logger.info("Начальные данные: %s", ", ".join(f"{k}={v}" for k, v in result.items()))
    return result


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    asyncio.run(_run())


async def _run() -> None:
    try:
        await apply_seeds()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    main()
