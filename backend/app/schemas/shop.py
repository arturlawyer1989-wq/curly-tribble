"""Публичное представление настроек магазина для витрины."""

import re

from pydantic import BaseModel, ConfigDict, computed_field


def phone_to_href(phone: str) -> str:
    """Превращает «+7 959 000-00-00» в ссылку tel:+79590000000. Пустой номер даёт пустую ссылку."""
    digits = re.sub(r"\D", "", phone)
    if not digits:
        return ""
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    if len(digits) == 10:
        digits = "7" + digits
    return f"tel:+{digits}"


class ShopPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    short_name: str
    city: str
    phone: str
    address: str
    work_hours: str
    legal_name: str
    inn: str
    email: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def phone_href(self) -> str:
        return phone_to_href(self.phone)
