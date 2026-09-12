"""Пароли и токены доступа для панели управления."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

# Argon2id с параметрами по умолчанию библиотеки: стойко и достаточно быстро для входа в админку
_hasher = PasswordHasher()

ACCESS_TOKEN_TYPE = "access"


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def password_needs_rehash(password_hash: str) -> bool:
    return _hasher.check_needs_rehash(password_hash)


class TokenError(Exception):
    """Токен не подходит: подделан, просрочен или не того типа."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason  # "expired" или "invalid"


def create_access_token(*, secret: str, user_id: int, role: str, login: str, lifetime: timedelta) -> tuple[str, datetime]:
    """Короткоживущий подписанный токен. Возвращает токен и момент истечения."""
    now = datetime.now(UTC)
    expires_at = now + lifetime
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "login": login,
        "type": ACCESS_TOKEN_TYPE,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": secrets.token_hex(8),
    }
    return jwt.encode(payload, secret, algorithm="HS256"), expires_at


def decode_access_token(token: str, *, secret: str) -> dict[str, Any]:
    """Проверить подпись и срок. При ошибке поднимает TokenError с причиной."""
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"], options={"require": ["exp", "sub", "type"]})
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("expired") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("invalid") from exc
    if payload.get("type") != ACCESS_TOKEN_TYPE:
        raise TokenError("invalid")
    return payload


def generate_refresh_token() -> str:
    """Случайная строка для обновления сессии. В базе хранится только её хеш."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
