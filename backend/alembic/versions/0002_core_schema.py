"""Полная схема базы под прототип: каталог, автомобили, схемы узлов, покупатели, заказы, цены, админка.

Ревизия: 0002
Предыдущая: 0001
Создана: 2026-09-12 22:51:21.012048+00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Расширение для триграммного поиска по названию товара
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    # Номера заказов начинаются с 2401, как в прототипе
    op.execute("CREATE SEQUENCE order_number_seq START WITH 2401")
    op.create_table('admin_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('login', sa.String(length=64), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=120), server_default='', nullable=False),
    sa.Column('role', sa.String(length=16), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("role IN ('owner', 'manager')", name='ck_admin_users_role'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('login')
    )
    op.create_table('brands',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('name_normalized', sa.String(length=120), nullable=False),
    sa.Column('country', sa.String(length=80), server_default='', nullable=False),
    sa.Column('rating', sa.SmallInteger(), server_default='0', nullable=False),
    sa.Column('is_oem', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('rating BETWEEN 0 AND 5', name='ck_brands_rating'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('name_normalized')
    )
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=160), nullable=False),
    sa.Column('slug', sa.String(length=160), nullable=False),
    sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
    sa.Column('icon', sa.String(length=40), server_default='', nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_categories_parent_id'), 'categories', ['parent_id'], unique=False)
    op.create_table('cross_references',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('brand_name', sa.String(length=120), nullable=False),
    sa.Column('brand_normalized', sa.String(length=120), nullable=False),
    sa.Column('article', sa.String(length=64), nullable=False),
    sa.Column('article_normalized', sa.String(length=64), nullable=False),
    sa.Column('cross_brand_name', sa.String(length=120), nullable=False),
    sa.Column('cross_brand_normalized', sa.String(length=120), nullable=False),
    sa.Column('cross_article', sa.String(length=64), nullable=False),
    sa.Column('cross_article_normalized', sa.String(length=64), nullable=False),
    sa.Column('source', sa.String(length=16), server_default='manual', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("source IN ('manual', 'import', 'supplier')", name='ck_cross_references_source'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('brand_normalized', 'article_normalized', 'cross_brand_normalized', 'cross_article_normalized', name='uq_cross_references_pair')
    )
    op.create_index('ix_cross_references_article', 'cross_references', ['article_normalized'], unique=False)
    op.create_index('ix_cross_references_cross_article', 'cross_references', ['cross_article_normalized'], unique=False)
    op.create_table('customers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=120), server_default='', nullable=False),
    sa.Column('status', sa.String(length=24), server_default='new', nullable=False),
    sa.Column('orders_count', sa.Integer(), server_default='0', nullable=False),
    sa.Column('pickups_count', sa.Integer(), server_default='0', nullable=False),
    sa.Column('refusals_count', sa.Integer(), server_default='0', nullable=False),
    sa.Column('refusal_streak', sa.Integer(), server_default='0', nullable=False),
    sa.Column('notify_channel', sa.String(length=8), server_default='sms', nullable=False),
    sa.Column('max_user_id', sa.String(length=64), server_default='', nullable=False),
    sa.Column('notes', sa.Text(), server_default='', nullable=False),
    sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("notify_channel IN ('sms', 'max')", name='ck_customers_notify_channel'),
    sa.CheckConstraint("status IN ('new', 'trusted', 'needs_confirmation', 'blocked')", name='ck_customers_status'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customers_phone'), 'customers', ['phone'], unique=True)
    op.create_table('delivery_zones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=8), nullable=False),
    sa.Column('title', sa.String(length=160), nullable=False),
    sa.Column('description', sa.String(length=255), server_default='', nullable=False),
    sa.Column('kind', sa.String(length=16), nullable=False),
    sa.Column('price', sa.Numeric(precision=10, scale=2), server_default='0', nullable=False),
    sa.Column('free_from', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.CheckConstraint("kind IN ('pickup', 'courier', 'route', 'other')", name='ck_delivery_zones_kind'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('otp_codes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.Column('purpose', sa.String(length=16), nullable=False),
    sa.Column('channel', sa.String(length=8), nullable=False),
    sa.Column('code_hash', sa.String(length=128), nullable=False),
    sa.Column('attempts', sa.SmallInteger(), server_default='0', nullable=False),
    sa.Column('max_attempts', sa.SmallInteger(), server_default='5', nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ip', sa.String(length=45), server_default='', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("channel IN ('sms', 'max')", name='ck_otp_codes_channel'),
    sa.CheckConstraint("purpose IN ('checkout', 'login', 'vin_request')", name='ck_otp_codes_purpose'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_otp_codes_phone_created', 'otp_codes', ['phone', 'created_at'], unique=False)
    op.create_table('scheme_systems',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('slug', sa.String(length=60), nullable=False),
    sa.Column('title', sa.String(length=120), nullable=False),
    sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('suppliers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=160), nullable=False),
    sa.Column('code', sa.String(length=40), nullable=False),
    sa.Column('contact_name', sa.String(length=120), server_default='', nullable=False),
    sa.Column('phone', sa.String(length=32), server_default='', nullable=False),
    sa.Column('email', sa.String(length=255), server_default='', nullable=False),
    sa.Column('price_source_type', sa.String(length=16), server_default='manual', nullable=False),
    sa.Column('price_source_config', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('default_delivery_days', sa.SmallInteger(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_sync_note', sa.Text(), server_default='', nullable=False),
    sa.Column('notes', sa.Text(), server_default='', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("price_source_type IN ('manual', 'email', 'url', 'api')", name='ck_suppliers_price_source_type'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code'),
    sa.UniqueConstraint('name')
    )
    op.create_table('vehicle_brands',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('slug', sa.String(length=80), nullable=False),
    sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
    sa.Column('is_popular', sa.Boolean(), server_default='false', nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('admin_audit_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('admin_id', sa.Integer(), nullable=True),
    sa.Column('action', sa.String(length=64), nullable=False),
    sa.Column('entity', sa.String(length=64), server_default='', nullable=False),
    sa.Column('entity_id', sa.String(length=64), server_default='', nullable=False),
    sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('ip', sa.String(length=45), server_default='', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['admin_id'], ['admin_users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_audit_log_admin_id'), 'admin_audit_log', ['admin_id'], unique=False)
    op.create_index('ix_admin_audit_log_created', 'admin_audit_log', ['created_at'], unique=False)
    op.create_table('admin_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token_hash', sa.String(length=64), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('user_agent', sa.String(length=255), server_default='', nullable=False),
    sa.Column('ip', sa.String(length=45), server_default='', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['admin_users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token_hash')
    )
    op.create_index(op.f('ix_admin_sessions_user_id'), 'admin_sessions', ['user_id'], unique=False)
    op.create_table('blacklist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.Column('reason', sa.Text(), server_default='', nullable=False),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['admin_users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone')
    )
    op.create_table('import_templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('supplier_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=160), nullable=False),
    sa.Column('file_format', sa.String(length=8), nullable=False),
    sa.Column('sheet_name', sa.String(length=80), server_default='', nullable=False),
    sa.Column('header_row', sa.SmallInteger(), server_default='1', nullable=False),
    sa.Column('delimiter', sa.String(length=4), server_default=';', nullable=False),
    sa.Column('encoding', sa.String(length=24), server_default='utf-8', nullable=False),
    sa.Column('column_map', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("file_format IN ('xlsx', 'csv')", name='ck_import_templates_file_format'),
    sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_import_templates_supplier_id'), 'import_templates', ['supplier_id'], unique=False)
    op.create_table('markup_rules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('kind', sa.String(length=16), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('brand_id', sa.Integer(), nullable=True),
    sa.Column('supplier_id', sa.Integer(), nullable=True),
    sa.Column('percent', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('rounding', sa.SmallInteger(), server_default='10', nullable=False),
    sa.Column('priority', sa.Integer(), server_default='0', nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("kind IN ('global', 'category', 'brand', 'supplier')", name='ck_markup_rules_kind'),
    sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('number', sa.Integer(), server_default=sa.text("nextval('order_number_seq')"), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=16), server_default='new', nullable=False),
    sa.Column('delivery_kind', sa.String(length=16), nullable=False),
    sa.Column('delivery_zone_id', sa.Integer(), nullable=True),
    sa.Column('delivery_address', sa.String(length=255), server_default='', nullable=False),
    sa.Column('customer_name', sa.String(length=120), server_default='', nullable=False),
    sa.Column('customer_phone', sa.String(length=20), nullable=False),
    sa.Column('comment', sa.Text(), server_default='', nullable=False),
    sa.Column('notify_channel', sa.String(length=8), server_default='sms', nullable=False),
    sa.Column('subtotal', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
    sa.Column('delivery_cost', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('total', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
    sa.Column('phone_confirmed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('idempotency_key', sa.String(length=64), nullable=True),
    sa.Column('issued_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("delivery_kind IN ('pickup', 'point', 'courier')", name='ck_orders_delivery_kind'),
    sa.CheckConstraint("notify_channel IN ('sms', 'max')", name='ck_orders_notify_channel'),
    sa.CheckConstraint("status IN ('new', 'processing', 'confirmed', 'ordered', 'arrived', 'issued', 'refused', 'cancelled')", name='ck_orders_status'),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['delivery_zone_id'], ['delivery_zones.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('idempotency_key'),
    sa.UniqueConstraint('number')
    )
    op.create_index(op.f('ix_orders_customer_id'), 'orders', ['customer_id'], unique=False)
    op.create_index('ix_orders_status_created', 'orders', ['status', 'created_at'], unique=False)
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('brand_id', sa.Integer(), nullable=False),
    sa.Column('article', sa.String(length=64), nullable=False),
    sa.Column('article_normalized', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('oem_number', sa.String(length=64), server_default='', nullable=False),
    sa.Column('oem_number_normalized', sa.String(length=64), server_default='', nullable=False),
    sa.Column('is_original', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('description', sa.Text(), server_default='', nullable=False),
    sa.Column('specs', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('barcode', sa.String(length=32), server_default='', nullable=False),
    sa.Column('unit', sa.String(length=16), server_default='шт', nullable=False),
    sa.Column('country', sa.String(length=80), server_default='', nullable=False),
    sa.Column('purchase_price', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('fixed_price', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('price_is_fixed', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('stock_qty', sa.Integer(), server_default='0', nullable=False),
    sa.Column('delivery_days', sa.SmallInteger(), nullable=True),
    sa.Column('supplier_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('stock_qty >= 0', name='ck_products_stock_qty'),
    sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('brand_id', 'article_normalized', name='uq_products_brand_article')
    )
    op.create_index('ix_products_article_normalized', 'products', ['article_normalized'], unique=False)
    op.create_index('ix_products_barcode', 'products', ['barcode'], unique=False)
    op.create_index(op.f('ix_products_brand_id'), 'products', ['brand_id'], unique=False)
    op.create_index(op.f('ix_products_category_id'), 'products', ['category_id'], unique=False)
    op.create_index('ix_products_name_trgm', 'products', ['name'], unique=False, postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'})
    op.create_index('ix_products_oem_number_normalized', 'products', ['oem_number_normalized'], unique=False)
    op.create_index(op.f('ix_products_supplier_id'), 'products', ['supplier_id'], unique=False)
    op.create_table('schemes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('system_id', sa.Integer(), nullable=False),
    sa.Column('slug', sa.String(length=80), nullable=False),
    sa.Column('title', sa.String(length=160), nullable=False),
    sa.Column('description', sa.Text(), server_default='', nullable=False),
    sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.ForeignKeyConstraint(['system_id'], ['scheme_systems.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_schemes_system_id'), 'schemes', ['system_id'], unique=False)
    op.create_table('vehicle_models',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('brand_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('slug', sa.String(length=120), nullable=False),
    sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
    sa.ForeignKeyConstraint(['brand_id'], ['vehicle_brands.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('brand_id', 'slug', name='uq_vehicle_models_brand_slug')
    )
    op.create_index(op.f('ix_vehicle_models_brand_id'), 'vehicle_models', ['brand_id'], unique=False)
    op.create_table('import_runs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('supplier_id', sa.Integer(), nullable=False),
    sa.Column('template_id', sa.Integer(), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.String(length=16), server_default='running', nullable=False),
    sa.Column('file_name', sa.String(length=255), server_default='', nullable=False),
    sa.Column('rows_total', sa.Integer(), server_default='0', nullable=False),
    sa.Column('rows_new', sa.Integer(), server_default='0', nullable=False),
    sa.Column('rows_updated', sa.Integer(), server_default='0', nullable=False),
    sa.Column('rows_deactivated', sa.Integer(), server_default='0', nullable=False),
    sa.Column('error', sa.Text(), server_default='', nullable=False),
    sa.CheckConstraint("status IN ('running', 'done', 'failed')", name='ck_import_runs_status'),
    sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['template_id'], ['import_templates.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_import_runs_supplier_id'), 'import_runs', ['supplier_id'], unique=False)
    op.create_table('order_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('position', sa.SmallInteger(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('brand_name', sa.String(length=120), nullable=False),
    sa.Column('article', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('is_original', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('qty', sa.Integer(), nullable=False),
    sa.Column('price', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('purchase_price', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('supplier_id', sa.Integer(), nullable=True),
    sa.Column('availability', sa.String(length=32), server_default='', nullable=False),
    sa.Column('status', sa.String(length=16), server_default='waiting', nullable=False),
    sa.Column('barcode', sa.String(length=32), nullable=True),
    sa.Column('storage_cell', sa.String(length=16), server_default='', nullable=False),
    sa.Column('arrived_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('issued_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint("status IN ('waiting', 'ordered', 'arrived', 'issued', 'cancelled')", name='ck_order_items_status'),
    sa.CheckConstraint('qty > 0', name='ck_order_items_qty'),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('barcode'),
    sa.UniqueConstraint('order_id', 'position', name='uq_order_items_position')
    )
    op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_items_product_id'), 'order_items', ['product_id'], unique=False)
    op.create_table('order_status_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('from_status', sa.String(length=16), nullable=True),
    sa.Column('to_status', sa.String(length=16), nullable=False),
    sa.Column('changed_by_admin_id', sa.Integer(), nullable=True),
    sa.Column('source', sa.String(length=16), server_default='system', nullable=False),
    sa.Column('comment', sa.Text(), server_default='', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("source IN ('admin', 'customer', 'system')", name='ck_order_status_log_source'),
    sa.ForeignKeyConstraint(['changed_by_admin_id'], ['admin_users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_order_status_log_order_created', 'order_status_log', ['order_id', 'created_at'], unique=False)
    op.create_table('product_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('file_path', sa.String(length=255), nullable=False),
    sa.Column('alt', sa.String(length=255), server_default='', nullable=False),
    sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_images_product_id'), 'product_images', ['product_id'], unique=False)
    op.create_table('scheme_points',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('scheme_id', sa.Integer(), nullable=False),
    sa.Column('number', sa.SmallInteger(), nullable=False),
    sa.Column('name', sa.String(length=160), nullable=False),
    sa.Column('short_name', sa.String(length=80), server_default='', nullable=False),
    sa.Column('shape_key', sa.String(length=40), server_default='kit', nullable=False),
    sa.Column('oem_number', sa.String(length=64), server_default='', nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['scheme_id'], ['schemes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('scheme_id', 'number', name='uq_scheme_points_number')
    )
    op.create_index(op.f('ix_scheme_points_category_id'), 'scheme_points', ['category_id'], unique=False)
    op.create_index(op.f('ix_scheme_points_scheme_id'), 'scheme_points', ['scheme_id'], unique=False)
    op.create_table('vehicle_generations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('model_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('code', sa.String(length=40), server_default='', nullable=False),
    sa.Column('year_from', sa.SmallInteger(), nullable=True),
    sa.Column('year_to', sa.SmallInteger(), nullable=True),
    sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
    sa.ForeignKeyConstraint(['model_id'], ['vehicle_models.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vehicle_generations_model_id'), 'vehicle_generations', ['model_id'], unique=False)
    op.create_table('scheme_point_fitments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('point_id', sa.Integer(), nullable=False),
    sa.Column('generation_id', sa.Integer(), nullable=False),
    sa.Column('oem_number', sa.String(length=64), nullable=False),
    sa.ForeignKeyConstraint(['generation_id'], ['vehicle_generations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['point_id'], ['scheme_points.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('point_id', 'generation_id', name='uq_scheme_point_fitments')
    )
    op.create_index(op.f('ix_scheme_point_fitments_generation_id'), 'scheme_point_fitments', ['generation_id'], unique=False)
    op.create_index(op.f('ix_scheme_point_fitments_point_id'), 'scheme_point_fitments', ['point_id'], unique=False)
    op.create_table('vehicle_modifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('generation_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('engine_code', sa.String(length=40), server_default='', nullable=False),
    sa.Column('power_hp', sa.SmallInteger(), nullable=True),
    sa.Column('fuel', sa.String(length=16), server_default='', nullable=False),
    sa.Column('body', sa.String(length=40), server_default='', nullable=False),
    sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
    sa.ForeignKeyConstraint(['generation_id'], ['vehicle_generations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vehicle_modifications_generation_id'), 'vehicle_modifications', ['generation_id'], unique=False)
    op.create_table('garage_vehicles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('generation_id', sa.Integer(), nullable=True),
    sa.Column('modification_id', sa.Integer(), nullable=True),
    sa.Column('label', sa.String(length=160), nullable=False),
    sa.Column('year', sa.SmallInteger(), nullable=True),
    sa.Column('vin', sa.String(length=17), server_default='', nullable=False),
    sa.Column('is_primary', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['generation_id'], ['vehicle_generations.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['modification_id'], ['vehicle_modifications.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_garage_vehicles_customer_id'), 'garage_vehicles', ['customer_id'], unique=False)
    op.create_table('product_fitments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('generation_id', sa.Integer(), nullable=False),
    sa.Column('modification_id', sa.Integer(), nullable=True),
    sa.Column('note', sa.String(length=255), server_default='', nullable=False),
    sa.ForeignKeyConstraint(['generation_id'], ['vehicle_generations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['modification_id'], ['vehicle_modifications.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('product_id', 'generation_id', 'modification_id', name='uq_product_fitments', postgresql_nulls_not_distinct=True)
    )
    op.create_index(op.f('ix_product_fitments_generation_id'), 'product_fitments', ['generation_id'], unique=False)
    op.create_index(op.f('ix_product_fitments_modification_id'), 'product_fitments', ['modification_id'], unique=False)
    op.create_index(op.f('ix_product_fitments_product_id'), 'product_fitments', ['product_id'], unique=False)
    op.create_table('vin_patterns',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('prefix', sa.String(length=17), nullable=False),
    sa.Column('modification_id', sa.Integer(), nullable=False),
    sa.Column('note', sa.String(length=255), server_default='', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['modification_id'], ['vehicle_modifications.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('prefix')
    )
    op.create_index(op.f('ix_vin_patterns_modification_id'), 'vin_patterns', ['modification_id'], unique=False)
    op.create_table('vin_requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.Column('vin', sa.String(length=17), nullable=False),
    sa.Column('modification_id', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('photo_path', sa.String(length=255), server_default='', nullable=False),
    sa.Column('status', sa.String(length=16), server_default='new', nullable=False),
    sa.Column('manager_note', sa.Text(), server_default='', nullable=False),
    sa.Column('phone_confirmed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('new', 'in_progress', 'answered', 'closed')", name='ck_vin_requests_status'),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['modification_id'], ['vehicle_modifications.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vin_requests_customer_id'), 'vin_requests', ['customer_id'], unique=False)
    op.create_index('ix_vin_requests_status_created', 'vin_requests', ['status', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_vin_requests_status_created', table_name='vin_requests')
    op.drop_index(op.f('ix_vin_requests_customer_id'), table_name='vin_requests')
    op.drop_table('vin_requests')
    op.drop_index(op.f('ix_vin_patterns_modification_id'), table_name='vin_patterns')
    op.drop_table('vin_patterns')
    op.drop_index(op.f('ix_product_fitments_product_id'), table_name='product_fitments')
    op.drop_index(op.f('ix_product_fitments_modification_id'), table_name='product_fitments')
    op.drop_index(op.f('ix_product_fitments_generation_id'), table_name='product_fitments')
    op.drop_table('product_fitments')
    op.drop_index(op.f('ix_garage_vehicles_customer_id'), table_name='garage_vehicles')
    op.drop_table('garage_vehicles')
    op.drop_index(op.f('ix_vehicle_modifications_generation_id'), table_name='vehicle_modifications')
    op.drop_table('vehicle_modifications')
    op.drop_index(op.f('ix_scheme_point_fitments_point_id'), table_name='scheme_point_fitments')
    op.drop_index(op.f('ix_scheme_point_fitments_generation_id'), table_name='scheme_point_fitments')
    op.drop_table('scheme_point_fitments')
    op.drop_index(op.f('ix_vehicle_generations_model_id'), table_name='vehicle_generations')
    op.drop_table('vehicle_generations')
    op.drop_index(op.f('ix_scheme_points_scheme_id'), table_name='scheme_points')
    op.drop_index(op.f('ix_scheme_points_category_id'), table_name='scheme_points')
    op.drop_table('scheme_points')
    op.drop_index(op.f('ix_product_images_product_id'), table_name='product_images')
    op.drop_table('product_images')
    op.drop_index('ix_order_status_log_order_created', table_name='order_status_log')
    op.drop_table('order_status_log')
    op.drop_index(op.f('ix_order_items_product_id'), table_name='order_items')
    op.drop_index(op.f('ix_order_items_order_id'), table_name='order_items')
    op.drop_table('order_items')
    op.drop_index(op.f('ix_import_runs_supplier_id'), table_name='import_runs')
    op.drop_table('import_runs')
    op.drop_index(op.f('ix_vehicle_models_brand_id'), table_name='vehicle_models')
    op.drop_table('vehicle_models')
    op.drop_index(op.f('ix_schemes_system_id'), table_name='schemes')
    op.drop_table('schemes')
    op.drop_index(op.f('ix_products_supplier_id'), table_name='products')
    op.drop_index('ix_products_oem_number_normalized', table_name='products')
    op.drop_index('ix_products_name_trgm', table_name='products', postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'})
    op.drop_index(op.f('ix_products_category_id'), table_name='products')
    op.drop_index(op.f('ix_products_brand_id'), table_name='products')
    op.drop_index('ix_products_barcode', table_name='products')
    op.drop_index('ix_products_article_normalized', table_name='products')
    op.drop_table('products')
    op.drop_index('ix_orders_status_created', table_name='orders')
    op.drop_index(op.f('ix_orders_customer_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_table('markup_rules')
    op.drop_index(op.f('ix_import_templates_supplier_id'), table_name='import_templates')
    op.drop_table('import_templates')
    op.drop_table('blacklist')
    op.drop_index(op.f('ix_admin_sessions_user_id'), table_name='admin_sessions')
    op.drop_table('admin_sessions')
    op.drop_index('ix_admin_audit_log_created', table_name='admin_audit_log')
    op.drop_index(op.f('ix_admin_audit_log_admin_id'), table_name='admin_audit_log')
    op.drop_table('admin_audit_log')
    op.drop_table('vehicle_brands')
    op.drop_table('suppliers')
    op.drop_table('scheme_systems')
    op.drop_index('ix_otp_codes_phone_created', table_name='otp_codes')
    op.drop_table('otp_codes')
    op.drop_table('delivery_zones')
    op.drop_index(op.f('ix_customers_phone'), table_name='customers')
    op.drop_table('customers')
    op.drop_index('ix_cross_references_cross_article', table_name='cross_references')
    op.drop_index('ix_cross_references_article', table_name='cross_references')
    op.drop_table('cross_references')
    op.drop_index(op.f('ix_categories_parent_id'), table_name='categories')
    op.drop_table('categories')
    op.drop_table('brands')
    op.drop_table('admin_users')
    op.execute("DROP SEQUENCE IF EXISTS order_number_seq")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
