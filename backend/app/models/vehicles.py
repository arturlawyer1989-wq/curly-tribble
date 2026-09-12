"""Справочник автомобилей: марка, модель, поколение, модификация; применяемость; шаблоны VIN."""

from sqlalchemy import Boolean, ForeignKey, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import CreatedAtMixin


class VehicleBrand(Base):
    __tablename__ = "vehicle_brands"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    models: Mapped[list["VehicleModel"]] = relationship(back_populates="brand", cascade="all, delete-orphan")


class VehicleModel(Base):
    __tablename__ = "vehicle_models"
    __table_args__ = (UniqueConstraint("brand_id", "slug", name="uq_vehicle_models_brand_slug"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("vehicle_brands.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(120))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    brand: Mapped[VehicleBrand] = relationship(back_populates="models")
    generations: Mapped[list["VehicleGeneration"]] = relationship(back_populates="model", cascade="all, delete-orphan")


class VehicleGeneration(Base):
    """Поколение: «2004–2013 (J200)»."""

    __tablename__ = "vehicle_generations"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("vehicle_models.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    code: Mapped[str] = mapped_column(String(40), default="", server_default="")
    year_from: Mapped[int | None] = mapped_column(SmallInteger)
    year_to: Mapped[int | None] = mapped_column(SmallInteger)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    model: Mapped[VehicleModel] = relationship(back_populates="generations")
    modifications: Mapped[list["VehicleModification"]] = relationship(back_populates="generation", cascade="all, delete-orphan")


class VehicleModification(Base):
    """Модификация: «1.6 16V, 109 л.с., F16D3»."""

    __tablename__ = "vehicle_modifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    generation_id: Mapped[int] = mapped_column(ForeignKey("vehicle_generations.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    engine_code: Mapped[str] = mapped_column(String(40), default="", server_default="")
    power_hp: Mapped[int | None] = mapped_column(SmallInteger)
    fuel: Mapped[str] = mapped_column(String(16), default="", server_default="")
    body: Mapped[str] = mapped_column(String(40), default="", server_default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    generation: Mapped[VehicleGeneration] = relationship(back_populates="modifications")


class ProductFitment(Base):
    """Применяемость товара: к поколению целиком или к конкретной модификации."""

    __tablename__ = "product_fitments"
    __table_args__ = (
        UniqueConstraint("product_id", "generation_id", "modification_id", name="uq_product_fitments", postgresql_nulls_not_distinct=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    generation_id: Mapped[int] = mapped_column(ForeignKey("vehicle_generations.id", ondelete="CASCADE"), index=True)
    modification_id: Mapped[int | None] = mapped_column(ForeignKey("vehicle_modifications.id", ondelete="CASCADE"), index=True)
    note: Mapped[str] = mapped_column(String(255), default="", server_default="")


class VinPattern(CreatedAtMixin, Base):
    """Начало VIN, по которому определяется модификация. Пополняется менеджером по мере заявок."""

    __tablename__ = "vin_patterns"

    id: Mapped[int] = mapped_column(primary_key=True)
    prefix: Mapped[str] = mapped_column(String(17), unique=True)
    modification_id: Mapped[int] = mapped_column(ForeignKey("vehicle_modifications.id", ondelete="CASCADE"), index=True)
    note: Mapped[str] = mapped_column(String(255), default="", server_default="")
