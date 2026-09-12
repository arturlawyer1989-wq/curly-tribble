"""Таблица настроек магазина.

Ревизия: 0001
Предыдущая: нет
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "shop_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("short_name", sa.String(length=16), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("phone", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("address", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("work_hours", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("legal_name", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("inn", sa.String(length=12), nullable=False, server_default=""),
        sa.Column("email", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("id = 1", name="ck_shop_settings_single_row"),
    )


def downgrade() -> None:
    op.drop_table("shop_settings")
