"""Сводка панели управления: сколько чего в базе, и список сотрудников."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin.deps import CurrentAdmin, get_current_admin, require_owner
from app.core.db import get_session
from app.models import (
    AdminUser,
    Brand,
    CrossReference,
    Customer,
    DeliveryZone,
    ImportTemplate,
    MarkupRule,
    Order,
    Product,
    Scheme,
    Supplier,
    VinRequest,
)
from app.models.enums import ORDER_STATUSES
from app.schemas.admin import AdminUserPublic, OverviewResponse, OverviewSection

router = APIRouter(tags=["Панель: сводка"])

# Разделы панели и таблицы, по которым считаются записи
SECTIONS = (
    ("orders", "Заказы", Order),
    ("vin-requests", "Заявки по VIN", VinRequest),
    ("products", "Товары и цены", Product),
    ("brands", "Бренды", Brand),
    ("schemes", "Схемы узлов", Scheme),
    ("suppliers", "Поставщики", Supplier),
    ("imports", "Импорт прайсов", ImportTemplate),
    ("cross-references", "Кросс-номера", CrossReference),
    ("customers", "Клиенты", Customer),
    ("delivery", "Доставка", DeliveryZone),
    ("pricing", "Наценки", MarkupRule),
)


@router.get("/overview", response_model=OverviewResponse, summary="Сводка по разделам")
async def overview(_: CurrentAdmin = Depends(get_current_admin), session: AsyncSession = Depends(get_session)) -> OverviewResponse:
    sections = []
    for key, title, model in SECTIONS:
        count = await session.scalar(select(func.count()).select_from(model))
        sections.append(OverviewSection(key=key, title=title, count=int(count or 0)))
    rows = (await session.execute(select(Order.status, func.count()).group_by(Order.status))).all()
    by_status = {status: 0 for status in ORDER_STATUSES}
    for status, count in rows:
        by_status[str(status)] = int(count)
    return OverviewResponse(sections=sections, orders_by_status=by_status)


@router.get("/users", response_model=list[AdminUserPublic], summary="Сотрудники (только владелец)")
async def list_users(_: CurrentAdmin = Depends(require_owner), session: AsyncSession = Depends(get_session)) -> list[AdminUserPublic]:
    users = (await session.scalars(select(AdminUser).order_by(AdminUser.id))).all()
    return [AdminUserPublic.model_validate(u) for u in users]
