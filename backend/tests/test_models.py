"""Схема базы: ограничения, последовательность номеров, индексы, триграммный поиск, начальные данные."""

from decimal import Decimal

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError

from app.core.db import get_session_factory
from app.models import (
    Brand,
    Customer,
    DeliveryZone,
    MarkupRule,
    Order,
    OrderItem,
    Product,
    ProductFitment,
    Scheme,
    SchemePoint,
    SchemeSystem,
    VehicleBrand,
    VehicleGeneration,
    VehicleModel,
)
from app.seeds.apply import apply_seeds


async def _customer(session, phone: str = "+79591234567") -> Customer:
    customer = Customer(phone=phone, name="Артур")
    session.add(customer)
    await session.flush()
    return customer


async def test_order_numbers_start_at_2401_and_increase() -> None:
    async with get_session_factory()() as session:
        customer = await _customer(session)
        first = Order(customer_id=customer.id, delivery_kind="pickup", customer_phone=customer.phone)
        second = Order(customer_id=customer.id, delivery_kind="pickup", customer_phone=customer.phone)
        session.add_all([first, second])
        await session.commit()
        numbers = sorted((await session.scalars(select(Order.number))).all())
    assert numbers == [2401, 2402]


async def test_product_article_is_unique_within_brand() -> None:
    async with get_session_factory()() as session:
        brand = Brand(name="TRW", name_normalized="TRW")
        session.add(brand)
        await session.flush()
        session.add(Product(brand_id=brand.id, article="GDB3332", article_normalized="GDB3332", name="Колодки"))
        await session.commit()
        session.add(Product(brand_id=brand.id, article="GDB 3332", article_normalized="GDB3332", name="Колодки ещё раз"))
        with pytest.raises(IntegrityError):
            await session.commit()


async def test_customer_phone_is_unique() -> None:
    async with get_session_factory()() as session:
        await _customer(session)
        await session.commit()
        session.add(Customer(phone="+79591234567"))
        with pytest.raises(IntegrityError):
            await session.commit()


async def test_order_status_must_be_known() -> None:
    async with get_session_factory()() as session:
        customer = await _customer(session)
        session.add(Order(customer_id=customer.id, delivery_kind="pickup", customer_phone=customer.phone, status="выдуманный"))
        with pytest.raises(IntegrityError):
            await session.commit()


async def test_order_items_are_deleted_with_order() -> None:
    async with get_session_factory()() as session:
        customer = await _customer(session)
        order = Order(customer_id=customer.id, delivery_kind="pickup", customer_phone=customer.phone)
        order.items.append(OrderItem(position=1, brand_name="MANN", article="W 712/94", name="Фильтр", qty=1, price=Decimal("480")))
        session.add(order)
        await session.commit()
        await session.delete(order)
        await session.commit()
        left = await session.scalar(select(func.count()).select_from(OrderItem))
    assert left == 0


async def test_fitment_without_modification_cannot_duplicate() -> None:
    async with get_session_factory()() as session:
        brand = Brand(name="GM", name_normalized="GM", is_oem=True)
        vbrand = VehicleBrand(name="Chevrolet", slug="chevrolet")
        session.add_all([brand, vbrand])
        await session.flush()
        model = VehicleModel(brand_id=vbrand.id, name="Lacetti", slug="lacetti")
        session.add(model)
        await session.flush()
        generation = VehicleGeneration(model_id=model.id, name="2004–2013 (J200)", code="J200", year_from=2004, year_to=2013)
        product = Product(brand_id=brand.id, article="96405129", article_normalized="96405129", name="Колодки передние", is_original=True)
        session.add_all([generation, product])
        await session.flush()
        session.add(ProductFitment(product_id=product.id, generation_id=generation.id, modification_id=None))
        await session.commit()
        session.add(ProductFitment(product_id=product.id, generation_id=generation.id, modification_id=None))
        with pytest.raises(IntegrityError):
            await session.commit()


async def test_required_indexes_and_extension_exist() -> None:
    async with get_session_factory()() as session:
        rows = (await session.execute(text("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'"))).scalars().all()
        extensions = (await session.execute(text("SELECT extname FROM pg_extension"))).scalars().all()
    for name in ("ix_products_article_normalized", "ix_customers_phone", "ix_orders_status_created", "ix_products_name_trgm"):
        assert name in rows, name
    assert "pg_trgm" in extensions


async def test_trigram_search_finds_misspelled_name() -> None:
    async with get_session_factory()() as session:
        brand = Brand(name="MANN-FILTER", name_normalized="MANNFILTER")
        session.add(brand)
        await session.flush()
        session.add_all([
            Product(brand_id=brand.id, article="W 712/94", article_normalized="W71294", name="Фильтр масляный"),
            Product(brand_id=brand.id, article="C 25 108", article_normalized="C25108", name="Фильтр воздушный"),
            Product(brand_id=brand.id, article="K015603XS", article_normalized="K015603XS", name="Ремень ГРМ, комплект"),
        ])
        await session.commit()
        found = (await session.execute(text("SELECT name FROM products WHERE similarity(name, :q) > 0.3 ORDER BY similarity(name, :q) DESC"), {"q": "фильтр маслянный"})).scalars().all()
    assert found[0] == "Фильтр масляный"
    assert "Ремень ГРМ, комплект" not in found


async def test_seeds_fill_reference_data_once() -> None:
    first = await apply_seeds()
    second = await apply_seeds()
    assert first["delivery_zones_added"] == 5 and first["vehicle_brands_added"] == 18
    assert (first["scheme_systems_added"], first["schemes_added"], first["scheme_points_added"]) == (10, 43, 206)
    assert first["markup_rule_created"] == 1
    assert all(value == 0 for value in second.values())
    async with get_session_factory()() as session:
        zones = await session.scalar(select(func.count()).select_from(DeliveryZone))
        brands = await session.scalar(select(func.count()).select_from(VehicleBrand))
        systems = await session.scalar(select(func.count()).select_from(SchemeSystem))
        schemes = await session.scalar(select(func.count()).select_from(Scheme))
        points = await session.scalar(select(func.count()).select_from(SchemePoint))
        rules = await session.scalar(select(func.count()).select_from(MarkupRule))
    assert (zones, brands, systems, schemes, points, rules) == (5, 18, 10, 43, 206, 1)
