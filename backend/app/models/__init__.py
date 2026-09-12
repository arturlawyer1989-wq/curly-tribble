"""Все таблицы базы данных. Импорт здесь нужен, чтобы Alembic видел модели."""

from app.core.db import Base
from app.models.admin import AdminAuditLog, AdminSession, AdminUser
from app.models.catalog import Brand, Category, CrossReference, Product, ProductImage, Supplier
from app.models.customers import BlacklistEntry, Customer, GarageVehicle, OtpCode
from app.models.orders import DeliveryZone, Order, OrderItem, OrderStatusLog, VinRequest
from app.models.pricing import ImportRun, ImportTemplate, MarkupRule
from app.models.schemes import Scheme, SchemePoint, SchemePointFitment, SchemeSystem
from app.models.shop import ShopSettings
from app.models.vehicles import ProductFitment, VehicleBrand, VehicleGeneration, VehicleModel, VehicleModification, VinPattern

__all__ = [
    "Base", "ShopSettings",
    "AdminAuditLog", "AdminSession", "AdminUser",
    "Brand", "Category", "CrossReference", "Product", "ProductImage", "Supplier",
    "BlacklistEntry", "Customer", "GarageVehicle", "OtpCode",
    "DeliveryZone", "Order", "OrderItem", "OrderStatusLog", "VinRequest",
    "ImportRun", "ImportTemplate", "MarkupRule",
    "Scheme", "SchemePoint", "SchemePointFitment", "SchemeSystem",
    "ProductFitment", "VehicleBrand", "VehicleGeneration", "VehicleModel", "VehicleModification", "VinPattern",
]
