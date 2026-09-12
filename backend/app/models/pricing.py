"""Правила наценки, шаблоны импорта прайсов и журнал импортов."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.enums import IMPORT_FORMATS, IMPORT_RUN_STATUSES, MARKUP_KINDS
from app.models.mixins import TimestampMixin, one_of


class MarkupRule(TimestampMixin, Base):
    """Наценка к закупочной цене: общая, по категории, по бренду или по поставщику."""

    __tablename__ = "markup_rules"
    __table_args__ = (one_of("kind", MARKUP_KINDS, "ck_markup_rules_kind"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(16))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    brand_id: Mapped[int | None] = mapped_column(ForeignKey("brands.id", ondelete="CASCADE"))
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"))
    percent: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    # Округление розничной цены вверх до указанного шага в рублях
    rounding: Mapped[int] = mapped_column(SmallInteger, default=10, server_default="10")
    priority: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")


class ImportTemplate(TimestampMixin, Base):
    """Как читать прайс поставщика: формат, лист, строка заголовка, соответствие колонок."""

    __tablename__ = "import_templates"
    __table_args__ = (one_of("file_format", IMPORT_FORMATS, "ck_import_templates_file_format"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    file_format: Mapped[str] = mapped_column(String(8))
    sheet_name: Mapped[str] = mapped_column(String(80), default="", server_default="")
    header_row: Mapped[int] = mapped_column(SmallInteger, default=1, server_default="1")
    delimiter: Mapped[str] = mapped_column(String(4), default=";", server_default=";")
    encoding: Mapped[str] = mapped_column(String(24), default="utf-8", server_default="utf-8")
    # {"brand": "A", "article": "B", "name": "C", "price": "D", "qty": "E"}
    column_map: Mapped[dict] = mapped_column(JSONB, default=dict, server_default=text("'{}'::jsonb"))


class ImportRun(Base):
    """Один запуск импорта прайса и его итоги."""

    __tablename__ = "import_runs"
    __table_args__ = (one_of("status", IMPORT_RUN_STATUSES, "ck_import_runs_status"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"), index=True)
    template_id: Mapped[int | None] = mapped_column(ForeignKey("import_templates.id", ondelete="SET NULL"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(16), default="running", server_default="running")
    file_name: Mapped[str] = mapped_column(String(255), default="", server_default="")
    rows_total: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    rows_new: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    rows_updated: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    rows_deactivated: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    error: Mapped[str] = mapped_column(Text, default="", server_default="")
