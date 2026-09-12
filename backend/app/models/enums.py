"""Допустимые значения статусов и видов. Хранятся строками, проверяются ограничениями базы."""

ADMIN_ROLES = ("owner", "manager")

PRICE_SOURCE_TYPES = ("manual", "email", "url", "api")
CROSS_SOURCES = ("manual", "import", "supplier")

CUSTOMER_STATUSES = ("new", "trusted", "needs_confirmation", "blocked")
NOTIFY_CHANNELS = ("sms", "max")

OTP_PURPOSES = ("checkout", "login", "vin_request")

DELIVERY_KINDS = ("pickup", "courier", "route", "other")
ORDER_DELIVERY_KINDS = ("pickup", "point", "courier")
ORDER_STATUSES = ("new", "processing", "confirmed", "ordered", "arrived", "issued", "refused", "cancelled")
ORDER_ITEM_STATUSES = ("waiting", "ordered", "arrived", "issued", "cancelled")
STATUS_LOG_SOURCES = ("admin", "customer", "system")
VIN_REQUEST_STATUSES = ("new", "in_progress", "answered", "closed")

MARKUP_KINDS = ("global", "category", "brand", "supplier")
IMPORT_FORMATS = ("xlsx", "csv")
IMPORT_RUN_STATUSES = ("running", "done", "failed")

# Русские названия статусов заказа для витрины и админки
ORDER_STATUS_TITLES = {
    "new": "Новый",
    "processing": "В обработке",
    "confirmed": "Цена подтверждена",
    "ordered": "В пути",
    "arrived": "Ожидает выдачи",
    "issued": "Выдан",
    "refused": "Невыкуп",
    "cancelled": "Отменён",
}
