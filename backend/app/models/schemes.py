"""Визуальный каталог: системы автомобиля, узлы со схемами и точки схем."""

from sqlalchemy import Boolean, ForeignKey, Integer, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class SchemeSystem(Base):
    """Система автомобиля: тормозная, подвеска, двигатель…"""

    __tablename__ = "scheme_systems"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    title: Mapped[str] = mapped_column(String(120))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    schemes: Mapped[list["Scheme"]] = relationship(back_populates="system", cascade="all, delete-orphan", order_by="Scheme.sort_order")


class Scheme(Base):
    """Узел со схемой: «Передний тормозной механизм»."""

    __tablename__ = "schemes"

    id: Mapped[int] = mapped_column(primary_key=True)
    system_id: Mapped[int] = mapped_column(ForeignKey("scheme_systems.id", ondelete="CASCADE"), index=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    system: Mapped[SchemeSystem] = relationship(back_populates="schemes")
    points: Mapped[list["SchemePoint"]] = relationship(back_populates="scheme", cascade="all, delete-orphan", order_by="SchemePoint.number")


class SchemePoint(Base):
    """Позиция на схеме: номер, название, форма для рисунка, оригинальный номер."""

    __tablename__ = "scheme_points"
    __table_args__ = (UniqueConstraint("scheme_id", "number", name="uq_scheme_points_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    scheme_id: Mapped[int] = mapped_column(ForeignKey("schemes.id", ondelete="CASCADE"), index=True)
    number: Mapped[int] = mapped_column(SmallInteger)
    name: Mapped[str] = mapped_column(String(160))
    short_name: Mapped[str] = mapped_column(String(80), default="", server_default="")
    shape_key: Mapped[str] = mapped_column(String(40), default="kit", server_default="kit")
    oem_number: Mapped[str] = mapped_column(String(64), default="", server_default="")
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), index=True)

    scheme: Mapped[Scheme] = relationship(back_populates="points")


class SchemePointFitment(Base):
    """Номер детали для позиции схемы под конкретное поколение автомобиля."""

    __tablename__ = "scheme_point_fitments"
    __table_args__ = (UniqueConstraint("point_id", "generation_id", name="uq_scheme_point_fitments"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    point_id: Mapped[int] = mapped_column(ForeignKey("scheme_points.id", ondelete="CASCADE"), index=True)
    generation_id: Mapped[int] = mapped_column(ForeignKey("vehicle_generations.id", ondelete="CASCADE"), index=True)
    oem_number: Mapped[str] = mapped_column(String(64))
