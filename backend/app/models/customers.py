"""Покупатели, их гараж, чёрный список и коды подтверждения."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.enums import CUSTOMER_STATUSES, NOTIFY_CHANNELS, OTP_PURPOSES
from app.models.mixins import CreatedAtMixin, TimestampMixin, one_of


class Customer(TimestampMixin, Base):
    """Покупатель. Ключ доступа: подтверждённый номер телефона."""

    __tablename__ = "customers"
    __table_args__ = (
        one_of("status", CUSTOMER_STATUSES, "ck_customers_status"),
        one_of("notify_channel", NOTIFY_CHANNELS, "ck_customers_notify_channel"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # Телефон в формате +79591234567
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), default="", server_default="")
    status: Mapped[str] = mapped_column(String(24), default="new", server_default="new")
    orders_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    pickups_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    refusals_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    # Отказы подряд: после двух заказ показывается владельцу с предупреждением
    refusal_streak: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    notify_channel: Mapped[str] = mapped_column(String(8), default="sms", server_default="sms")
    max_user_id: Mapped[str] = mapped_column(String(64), default="", server_default="")
    notes: Mapped[str] = mapped_column(Text, default="", server_default="")
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    garage: Mapped[list["GarageVehicle"]] = relationship(back_populates="customer", cascade="all, delete-orphan")


class GarageVehicle(CreatedAtMixin, Base):
    """Автомобиль в гараже покупателя."""

    __tablename__ = "garage_vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    generation_id: Mapped[int | None] = mapped_column(ForeignKey("vehicle_generations.id", ondelete="SET NULL"))
    modification_id: Mapped[int | None] = mapped_column(ForeignKey("vehicle_modifications.id", ondelete="SET NULL"))
    label: Mapped[str] = mapped_column(String(160))
    year: Mapped[int | None] = mapped_column(SmallInteger)
    vin: Mapped[str] = mapped_column(String(17), default="", server_default="")
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    customer: Mapped[Customer] = relationship(back_populates="garage")


class BlacklistEntry(CreatedAtMixin, Base):
    """Номера, с которых заказ оформить нельзя."""

    __tablename__ = "blacklist"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    reason: Mapped[str] = mapped_column(Text, default="", server_default="")
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("admin_users.id", ondelete="SET NULL"))


class OtpCode(CreatedAtMixin, Base):
    """Код подтверждения номера. Хранится только хеш кода."""

    __tablename__ = "otp_codes"
    __table_args__ = (
        Index("ix_otp_codes_phone_created", "phone", "created_at"),
        one_of("purpose", OTP_PURPOSES, "ck_otp_codes_purpose"),
        one_of("channel", NOTIFY_CHANNELS, "ck_otp_codes_channel"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    phone: Mapped[str] = mapped_column(String(20))
    purpose: Mapped[str] = mapped_column(String(16))
    channel: Mapped[str] = mapped_column(String(8))
    code_hash: Mapped[str] = mapped_column(String(128))
    attempts: Mapped[int] = mapped_column(SmallInteger, default=0, server_default="0")
    max_attempts: Mapped[int] = mapped_column(SmallInteger, default=5, server_default="5")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ip: Mapped[str] = mapped_column(String(45), default="", server_default="")
