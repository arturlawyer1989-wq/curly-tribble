"""Заказы, позиции, журнал статусов, заявки по VIN, зоны доставки."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, SmallInteger, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.enums import DELIVERY_KINDS, NOTIFY_CHANNELS, ORDER_DELIVERY_KINDS, ORDER_ITEM_STATUSES, ORDER_STATUSES, STATUS_LOG_SOURCES, VIN_REQUEST_STATUSES
from app.models.mixins import CreatedAtMixin, TimestampMixin, one_of

ORDER_NUMBER_SEQUENCE = "order_number_seq"
ORDER_NUMBER_START = 2401


class DeliveryZone(Base):
    """Куда возим и почём. Редактируется владельцем."""

    __tablename__ = "delivery_zones"
    __table_args__ = (one_of("kind", DELIVERY_KINDS, "ck_delivery_zones_kind"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(8), unique=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(String(255), default="", server_default="")
    kind: Mapped[str] = mapped_column(String(16))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"), server_default="0")
    # Сумма заказа, от которой доставка бесплатна
    free_from: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")


class Order(TimestampMixin, Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_status_created", "status", "created_at"),
        one_of("status", ORDER_STATUSES, "ck_orders_status"),
        one_of("delivery_kind", ORDER_DELIVERY_KINDS, "ck_orders_delivery_kind"),
        one_of("notify_channel", NOTIFY_CHANNELS, "ck_orders_notify_channel"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # Человеческий номер заказа из последовательности, начинается с 2401
    number: Mapped[int] = mapped_column(Integer, unique=True, server_default=text(f"nextval('{ORDER_NUMBER_SEQUENCE}')"))
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="RESTRICT"), index=True)
    status: Mapped[str] = mapped_column(String(16), default="new", server_default="new")
    delivery_kind: Mapped[str] = mapped_column(String(16))
    delivery_zone_id: Mapped[int | None] = mapped_column(ForeignKey("delivery_zones.id", ondelete="SET NULL"))
    delivery_address: Mapped[str] = mapped_column(String(255), default="", server_default="")
    customer_name: Mapped[str] = mapped_column(String(120), default="", server_default="")
    customer_phone: Mapped[str] = mapped_column(String(20))
    comment: Mapped[str] = mapped_column(Text, default="", server_default="")
    notify_channel: Mapped[str] = mapped_column(String(8), default="sms", server_default="sms")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"), server_default="0")
    delivery_cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"), server_default="0")
    phone_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Ключ повторной отправки формы: два нажатия «Оформить» дают один заказ
    idempotency_key: Mapped[str | None] = mapped_column(String(64), unique=True)
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan", order_by="OrderItem.position")
    status_log: Mapped[list["OrderStatusLog"]] = relationship(back_populates="order", cascade="all, delete-orphan", order_by="OrderStatusLog.created_at")


class OrderItem(Base):
    """Позиция заказа с копией данных товара на момент заказа."""

    __tablename__ = "order_items"
    __table_args__ = (
        UniqueConstraint("order_id", "position", name="uq_order_items_position"),
        CheckConstraint("qty > 0", name="ck_order_items_qty"),
        one_of("status", ORDER_ITEM_STATUSES, "ck_order_items_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(SmallInteger)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), index=True)
    brand_name: Mapped[str] = mapped_column(String(120))
    article: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(255))
    is_original: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    qty: Mapped[int] = mapped_column(Integer)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    purchase_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id", ondelete="SET NULL"))
    availability: Mapped[str] = mapped_column(String(32), default="", server_default="")
    status: Mapped[str] = mapped_column(String(16), default="waiting", server_default="waiting")
    # Штрихкод наклейки D24-{номер заказа}-{позиция}
    barcode: Mapped[str | None] = mapped_column(String(32), unique=True)
    storage_cell: Mapped[str] = mapped_column(String(16), default="", server_default="")
    arrived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    order: Mapped[Order] = relationship(back_populates="items")


class OrderStatusLog(CreatedAtMixin, Base):
    __tablename__ = "order_status_log"
    __table_args__ = (
        Index("ix_order_status_log_order_created", "order_id", "created_at"),
        one_of("source", STATUS_LOG_SOURCES, "ck_order_status_log_source"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    from_status: Mapped[str | None] = mapped_column(String(16))
    to_status: Mapped[str] = mapped_column(String(16))
    changed_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("admin_users.id", ondelete="SET NULL"))
    source: Mapped[str] = mapped_column(String(16), default="system", server_default="system")
    comment: Mapped[str] = mapped_column(Text, default="", server_default="")

    order: Mapped[Order] = relationship(back_populates="status_log")


class VinRequest(TimestampMixin, Base):
    """Заявка на ручной подбор по VIN."""

    __tablename__ = "vin_requests"
    __table_args__ = (
        Index("ix_vin_requests_status_created", "status", "created_at"),
        one_of("status", VIN_REQUEST_STATUSES, "ck_vin_requests_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), index=True)
    phone: Mapped[str] = mapped_column(String(20))
    vin: Mapped[str] = mapped_column(String(17))
    modification_id: Mapped[int | None] = mapped_column(ForeignKey("vehicle_modifications.id", ondelete="SET NULL"))
    description: Mapped[str] = mapped_column(Text)
    photo_path: Mapped[str] = mapped_column(String(255), default="", server_default="")
    status: Mapped[str] = mapped_column(String(16), default="new", server_default="new")
    manager_note: Mapped[str] = mapped_column(Text, default="", server_default="")
    phone_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
