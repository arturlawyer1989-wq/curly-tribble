"""Нормализация артикулов, брендов, телефонов и проверка VIN."""

from app.services.normalize import is_valid_vin, normalize_article, normalize_brand, normalize_phone


def test_article_variants_collapse_to_one_value() -> None:
    assert normalize_article("w 712/94") == "W71294"
    assert normalize_article("W-712/94") == "W71294"
    assert normalize_article("W71294") == "W71294"
    assert normalize_article("  96 405 129 ") == "96405129"
    assert normalize_article("0 986 494 573") == "0986494573"


def test_article_cyrillic_lookalikes_become_latin() -> None:
    # Русские А, В, С, Е, Н, К, М, О, Р, Т, Х в артикуле
    assert normalize_article("ВКR6Е-11") == "BKR6E11"
    assert normalize_article("ос 195") == "OC195"


def test_brand_normalization() -> None:
    assert normalize_brand("Mann-Filter") == normalize_brand("MANN FILTER") == "MANNFILTER"


def test_phone_formats() -> None:
    assert normalize_phone("+7 959 123-45-67") == "+79591234567"
    assert normalize_phone("8 (959) 123 45 67") == "+79591234567"
    assert normalize_phone("9591234567") == "+79591234567"
    assert normalize_phone("123") == ""
    assert normalize_phone("нет телефона") == ""


def test_vin_validation() -> None:
    assert is_valid_vin("KL1NF19EJ8K123456") is True
    assert is_valid_vin("kl1nf19ej8k123456") is True
    assert is_valid_vin("KL1NF19EJ8K12345") is False
    assert is_valid_vin("KL1NF19EJ8K12345O") is False
