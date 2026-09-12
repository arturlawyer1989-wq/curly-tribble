"""Каталог: бренды, категории, поставщики, товары, фото, кросс-номера."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, SmallInteger, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.enums import CROSS_SOURCES, PRICE_SOURCE_TYPES
from app.models.mixins import CreatedAtMixin, TimestampMixin, one_of


class Brand(TimestampMixin, Base):
    """Бренд запчастей (MANN-FILTER, TRW, GM)."""

    __tablename__ = "brands"
    __table_args__ = (CheckConstraint("rating BETWEEN 0 AND 5", name="ck_brands_rating"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    name_normalized: Mapped[str] = mapped_column(String(120), unique=True)
    country: Mapped[str] = mapped_column(String(80), default="", server_default="")
    # Рейтинг бренда 0..5 для сортировки «выше рейтинг бренда»
    rating: Mapped[int] = mapped_column(SmallInteger, default=0, server_default="0")
    # Бренд автопроизводителя: его детали считаются оригиналом
    is_oem: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")


class Category(Base):
    """Категория товаров, дерево любой глубины."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(160), unique=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    icon: Mapped[str] = mapped_column(String(40), default="", server_default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")


class Supplier(TimestampMixin, Base):
    """Поставщик и способ получения его прайса."""

    __tablename__ = "suppliers"
    __table_args__ = (one_of("price_source_type", PRICE_SOURCE_TYPES, "ck_suppliers_price_source_type"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True)
    code: Mapped[str] = mapped_column(String(40), unique=True)
    contact_name: Mapped[str] = mapped_column(String(120), default="", server_default="")
    phone: Mapped[str] = mapped_column(String(32), default="", server_default="")
    email: Mapped[str] = mapped_column(String(255), default="", server_default="")
    price_source_type: Mapped[str] = mapped_column(String(16), default="manual", server_default="manual")
    # Параметры источника: адрес ссылки, настройки почтового ящика, ключи API
    price_source_config: Mapped[dict] = mapped_column(JSONB, default=dict, server_default=text("'{}'::jsonb"))
    default_delivery_days: Mapped[int | None] = mapped_column(SmallInteger)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_sync_note: Mapped[str] = mapped_column(Text, default="", server_default="")
    notes: Mapped[str] = mapped_column(Text, default="", server_default="")


class Product(TimestampMixin, Base):
    """Товар: конкретный артикул конкретного бренда."""

    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("brand_id", "article_normalized", name="uq_products_brand_article"),
        Index("ix_products_article_normalized", "article_normalized"),
        Index("ix_products_oem_number_normalized", "oem_number_normalized"),
        Index("ix_products_barcode", "barcode"),
        # Триграммный индекс: поиск по названию с опечатками и по части слова
        Index("ix_products_name_trgm", "name", postgresql_using="gin", postgresql_ops={"name": "gin_trgm_ops"}),
        CheckConstraint("stock_qty >= 0", name="ck_products_stock_qty"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id", ondelete="RESTRICT"), index=True)
    article: Mapped[str] = mapped_column(String(64))
    article_normalized: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(255))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), index=True)
    # Оригинальный номер, которому соответствует деталь
    oem_number: Mapped[str] = mapped_column(String(64), default="", server_default="")
    oem_number_normalized: Mapped[str] = mapped_column(String(64), default="", server_default="")
    is_original: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    # Характеристики: {"Высота": "65 мм", ...}
    specs: Mapped[dict] = mapped_column(JSONB, default=dict, server_default=text("'{}'::jsonb"))
    barcode: Mapped[str] = mapped_column(String(32), default="", server_default="")
    unit: Mapped[str] = mapped_column(String(16), default="шт", server_default="шт")
    country: Mapped[str] = mapped_column(String(80), default="", server_default="")
    # Закупочная цена поставщика; розница считается по правилам наценки
    purchase_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    # Цена, поставленная владельцем вручную и защищённая от автообновления
    fixed_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    price_is_fixed: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    stock_qty: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    delivery_days: Mapped[int | None] = mapped_column(SmallInteger)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id", ondelete="SET NULL"), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    brand: Mapped[Brand] = relationship()
    images: Mapped[list["ProductImage"]] = relationship(back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.sort_order")


class ProductImage(CreatedAtMixin, Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    file_path: Mapped[str] = mapped_column(String(255))
    alt: Mapped[str] = mapped_column(String(255), default="", server_default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    product: Mapped[Product] = relationship(back_populates="images")


class CrossReference(CreatedAtMixin, Base):
    """Соответствие артикулов: бренд+артикул заменяет другой бренд+артикул. Обе стороны могут отсутствовать в каталоге."""

    __tablename__ = "cross_references"
    __table_args__ = (
        UniqueConstraint("brand_normalized", "article_normalized", "cross_brand_normalized", "cross_article_normalized", name="uq_cross_references_pair"),
        Index("ix_cross_references_article", "article_normalized"),
        Index("ix_cross_references_cross_article", "cross_article_normalized"),
        one_of("source", CROSS_SOURCES, "ck_cross_references_source"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_name: Mapped[str] = mapped_column(String(120))
    brand_normalized: Mapped[str] = mapped_column(String(120))
    article: Mapped[str] = mapped_column(String(64))
    article_normalized: Mapped[str] = mapped_column(String(64))
    cross_brand_name: Mapped[str] = mapped_column(String(120))
    cross_brand_normalized: Mapped[str] = mapped_column(String(120))
    cross_article: Mapped[str] = mapped_column(String(64))
    cross_article_normalized: Mapped[str] = mapped_column(String(64))
    source: Mapped[str] = mapped_column(String(16), default="manual", server_default="manual")
