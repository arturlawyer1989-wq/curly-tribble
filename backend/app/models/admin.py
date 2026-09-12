"""Сотрудники панели управления, их сессии и журнал действий."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.enums import ADMIN_ROLES
from app.models.mixins import CreatedAtMixin, TimestampMixin, one_of


class AdminUser(TimestampMixin, Base):
    """Сотрудник: владелец или менеджер."""

    __tablename__ = "admin_users"
    __table_args__ = (one_of("role", ADMIN_ROLES, "ck_admin_users_role"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(120), default="", server_default="")
    role: Mapped[str] = mapped_column(String(16))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    sessions: Mapped[list["AdminSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class AdminSession(CreatedAtMixin, Base):
    """Сессия обновления токена. Хранится хеш токена, сам токен только у браузера."""

    __tablename__ = "admin_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("admin_users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user_agent: Mapped[str] = mapped_column(String(255), default="", server_default="")
    ip: Mapped[str] = mapped_column(String(45), default="", server_default="")

    user: Mapped[AdminUser] = relationship(back_populates="sessions")


class AdminAuditLog(CreatedAtMixin, Base):
    """Кто, когда и что сделал в панели управления."""

    __tablename__ = "admin_audit_log"
    __table_args__ = (Index("ix_admin_audit_log_created", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int | None] = mapped_column(ForeignKey("admin_users.id", ondelete="SET NULL"), index=True)
    action: Mapped[str] = mapped_column(String(64))
    entity: Mapped[str] = mapped_column(String(64), default="", server_default="")
    entity_id: Mapped[str] = mapped_column(String(64), default="", server_default="")
    details: Mapped[dict] = mapped_column(JSONB, default=dict, server_default=text("'{}'::jsonb"))
    ip: Mapped[str] = mapped_column(String(45), default="", server_default="")
