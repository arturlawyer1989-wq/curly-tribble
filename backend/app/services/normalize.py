"""Нормализация артикулов, брендов и телефонов: одинаковые значения в разном написании должны совпадать."""

import re

# Кириллические буквы, похожие на латинские: в артикулах их часто путают
_CYRILLIC_TO_LATIN = str.maketrans({
    "А": "A", "В": "B", "С": "C", "Е": "E", "Н": "H", "К": "K", "М": "M", "О": "O",
    "Р": "P", "Т": "T", "Х": "X", "У": "Y", "І": "I",
})
_NOT_ALNUM = re.compile(r"[^A-Z0-9]+")
_NOT_DIGIT = re.compile(r"\D+")


def normalize_article(value: str) -> str:
    """«w 712/94», «W-712/94», «W71294» превращаются в «W71294»."""
    upper = value.strip().upper().translate(_CYRILLIC_TO_LATIN)
    return _NOT_ALNUM.sub("", upper)


def normalize_brand(value: str) -> str:
    """«Mann-Filter», «MANN FILTER», «mann filter» превращаются в «MANNFILTER»."""
    return normalize_article(value)


def normalize_phone(value: str) -> str:
    """Российский номер в формат +79591234567. Пустая строка, если это не похоже на номер."""
    digits = _NOT_DIGIT.sub("", value)
    if len(digits) == 11 and digits[0] in ("7", "8"):
        digits = "7" + digits[1:]
    elif len(digits) == 10:
        digits = "7" + digits
    else:
        return ""
    return "+" + digits


def is_valid_vin(value: str) -> bool:
    """VIN: 17 символов, латиница и цифры, без букв I, O, Q."""
    candidate = value.strip().upper()
    return len(candidate) == 17 and re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", candidate) is not None
