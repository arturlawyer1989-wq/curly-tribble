"""Настройки магазина: одна строка с реквизитами и контактами."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

SHOP_ROW_ID = 1


class ShopSettings(Base):
    __tablename__ = "shop_settings"
    __table_args__ = (CheckConstraint(f"id = {SHOP_ROW_ID}", name="ck_shop_settings_single_row"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    short_name: Mapped[str] = mapped_column(String(16))
    city: Mapped[str] = mapped_column(String(120), default="", server_default="")
    phone: Mapped[str] = mapped_column(String(32), default="", server_default="")
    address: Mapped[str] = mapped_column(String(255), default="", server_default="")
    work_hours: Mapped[str] = mapped_column(String(120), default="", server_default="")
    legal_name: Mapped[str] = mapped_column(String(255), default="", server_default="")
    inn: Mapped[str] = mapped_column(String(12), default="", server_default="")
    email: Mapped[str] = mapped_column(String(255), default="", server_default="")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
